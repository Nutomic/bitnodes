#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# export.py - Stores scan result in SQLite database and exports it into csv/text files
#
# Copyright (c) Addy Yeow Chin Heng <ayeowch@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

"""
Exports enumerated data for reachable nodes into CSV and TXT files.
"""

import logging
import os
import sys
import time
from binascii import hexlify, unhexlify
from ConfigParser import ConfigParser, NoOptionError
import unicodecsv as csv
import json
import urllib
import sqlite3
import utils

from utils import new_redis_conn

REDIS_CONN = None
CONF = {}


def get_row(node):
    """
    Returns enumerated row data from Redis for the specified node.
    """
    # address, port, version, user_agent, timestamp, services
    node = eval(node)
    address = node[0]
    port = node[1]
    services = node[-1]

    height = REDIS_CONN.get('height:{}-{}-{}'.format(address, port, services))
    if height is None:
        height = (0,)
    else:
        height = (int(height),)

    hostname = REDIS_CONN.hget('resolve:{}'.format(address), 'hostname')
    hostname = (hostname,)

    geoip = REDIS_CONN.hget('resolve:{}'.format(address), 'geoip')
    if geoip is None:
        # city, country, latitude, longitude, timezone, asn, org
        geoip = (None, None, 0.0, 0.0, None, None, None)
    else:
        geoip = eval(geoip)

    return node + height + hostname + geoip


def get_dash_masternode_addresses():
    """
    Returns IP:port list of all known masternodes (using the Dash Insight API)
    """
    url = CONF['dash_insight_api'] + '/masternodes/list'
    response = urllib.urlopen(url)
    masternodes = json.loads(response.read())
    enabled_masternodes = filter(lambda item: item['status'] == 'ENABLED', masternodes)
    return map(lambda item: item['ip'], enabled_masternodes)

def store_reachable_nodes(nodes, timestamp):
    """
    Stores all nodes that were discovered in the current crawl in an SQLite database
    """
    utils.create_folder_if_not_exists(os.path.dirname(CONF['storage_file']))
    connection = sqlite3.connect(CONF['storage_file'])
    cursor = connection.cursor()

    cursor.execute('CREATE TABLE IF NOT EXISTS ' + CONF['coin_name'] + '_nodes ' +
                   '(id INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                   'coin_name TEXT NOT NULL, ' +
                   'timestamp INT NOT NULL, ' +
                   'last_block INT NOT NULL, ' +
                   'node_address TEXT NOT NULL, '
                   'protocol_version INT NOT NULL, ' +
                   'client_version TEXT NOT NULL, ' +
                   'country TEXT,' +
                   'city TEXT, ' +
                   'isp_cloud TEXT, ' +
                   'is_masternode INT)')

    if CONF['dash_insight_api'] is not None:
        dash_masternodes = get_dash_masternode_addresses()
        is_dash = True
    else:
        dash_masternodes = None
        is_dash = False

    for node in nodes:
        row = get_row(node)
        address = "{}:{}".format(row[0], row[1])
        is_masternode = address in dash_masternodes if is_dash else None
        cursor.execute('INSERT INTO ' + CONF['coin_name'] + '_nodes (coin_name, ' +
                       'timestamp, last_block, node_address, protocol_version, ' +
                       'client_version, country, city, isp_cloud, is_masternode) '
                       'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                       [CONF['coin_name'], timestamp, row[6], address,
                        row[2], row[3], row[9], row[12], row[14], is_masternode])

    connection.commit()
    connection.close()


def export_nodes(timestamp):
    """
    Merges enumerated data for the specified nodes and exports them into
    timestamp-prefixed CSV and TXT files.
    """
    utils.create_folder_if_not_exists(CONF['export_dir'])
    base_path = os.path.join(CONF['export_dir'], "{}".format(timestamp))
    csv_path = base_path + ".csv"
    txt_path = base_path + ".txt"

    connection = sqlite3.connect(CONF['storage_file'])
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    # Select all nodes that have been online at least once in the last 24 hours
    nodes_online_24h = cursor.execute('SELECT * ' +
                                      'FROM ' + CONF['coin_name'] + '_nodes ' +
                                      'WHERE timestamp >= ?', [timestamp - 24 * 60 * 60])

    with open(csv_path, 'a') as csv_file, open(txt_path, 'a') as txt_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
        txt_writer = csv.writer(txt_file, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
        for row in nodes_online_24h:
            output_data = [
                row['node_address'],
                row['last_block'],
                row['protocol_version'],
                row['client_version'],
                row['country'],
                row['city'],
                row['isp_cloud']]

            if row['is_masternode'] is not None:
                output_data.append(row['is_masternode'])

            csv_writer.writerow(output_data)
            txt_writer.writerow(output_data)

    connection.close()
    logging.info("Wrote %s and %s", csv_path, txt_path)


def init_conf(argv):
    """
    Populates CONF with key-value pairs from configuration file.
    """
    conf = ConfigParser()
    conf.read(argv[1])
    CONF['coin_name'] = conf.get('general', 'coin_name')
    CONF['magic_number'] = unhexlify(conf.get('general', 'magic_number'))
    CONF['db'] = conf.getint('general', 'db')
    CONF['logfile'] = conf.get('export', 'logfile')
    CONF['debug'] = conf.getboolean('export', 'debug')
    CONF['export_dir'] = conf.get('export', 'export_dir')
    CONF['storage_file'] = conf.get('export', 'storage_file')
    try:
        CONF['dash_insight_api'] = conf.get('export', 'dash_insight_api')
    except NoOptionError:
        CONF['dash_insight_api'] = None


def main(argv):
    if len(argv) < 2 or not os.path.exists(argv[1]):
        print("Usage: export.py [config]")
        return 1

    # Initialize global conf
    init_conf(argv)

    # Initialize logger
    loglevel = logging.INFO
    if CONF['debug']:
        loglevel = logging.DEBUG

    logformat = ("%(asctime)s,%(msecs)05.1f %(levelname)s (%(funcName)s) "
                 "%(message)s")
    logging.basicConfig(level=loglevel,
                        format=logformat,
                        filename=CONF['logfile'],
                        filemode='w')
    print("Log: {}, press CTRL+C to terminate..".format(CONF['logfile']))

    global REDIS_CONN
    REDIS_CONN = new_redis_conn(db=CONF['db'])

    subscribe_key = 'resolve:{}'.format(hexlify(CONF['magic_number']))
    publish_key = 'export:{}'.format(hexlify(CONF['magic_number']))

    pubsub = REDIS_CONN.pubsub()
    pubsub.subscribe(subscribe_key)
    while True:
        msg = pubsub.get_message()
        if msg is None:
            time.sleep(0.001)  # 1 ms artificial intrinsic latency.
            continue
        # 'resolve' message is published by resolve.py after resolving hostname
        # and GeoIP data for all reachable nodes.
        if msg['channel'] == subscribe_key and msg['type'] == 'message':
            timestamp = int(msg['data'])  # From ping.py's 'snapshot' message
            logging.info("Timestamp: %d", timestamp)
            nodes = REDIS_CONN.smembers('opendata')
            logging.info("Nodes: %d", len(nodes))
            store_reachable_nodes(nodes, timestamp)
            export_nodes(timestamp)
            REDIS_CONN.publish(publish_key, timestamp)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))