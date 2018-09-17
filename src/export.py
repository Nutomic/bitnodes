#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
# export.py - Stores scan result in SQLite database and exports it into csv/text files
#
# Copyright (c) Addy Yeow Chin Heng <ayeowch@gmail.com>
# Portions Copyright (c) 2018 Felix Ableitner
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

from __future__ import division
import logging
import os
import sys
import time
from binascii import hexlify
from ConfigParser import ConfigParser
import unicodecsv as csv
import json
import urllib
import sqlite3
import utils
import itertools
from utils import new_redis_conn

UPTIME_INTERVALS = {'uptime_two_hours': 2 * 60 * 60,
                    'uptime_eight_hours': 8 * 60 * 60,
                    'uptime_day': 24 * 60 * 60,
                    'uptime_seven_days': 7 * 24 * 60 * 60,
                    'uptime_thirty_days': 30 * 24 * 60 * 60}

REDIS_CONN = None
CONF = {}
coins_exported = {'bitcoin': 0, 'bitcoincash': 0, 'dash': 0, 'litecoin': 0}


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
        # city, country_iso, country_name, latitude, longitude, timezone, asn, org
        geoip = (None, None, None, 0.0, 0.0, None, None, None)
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
    start = time.time()
    utils.create_folder_if_not_exists(os.path.dirname(CONF['storage_file']))
    connection = sqlite3.connect(CONF['storage_file'], timeout=120)

    connection.execute('CREATE TABLE IF NOT EXISTS ' + CONF['coin_name'] + '_nodes ' +
                       '(id INTEGER PRIMARY KEY AUTOINCREMENT, ' +
                       'node_address TEXT NOT NULL, '
                       'timestamp INT NOT NULL, ' +
                       'last_block INT NOT NULL, ' +
                       'protocol_version INT NOT NULL, ' +
                       'client_version TEXT NOT NULL, ' +
                       'country_iso TEXT,' +
                       'country_name TEXT, ' +
                       'city TEXT, ' +
                       'isp_cloud TEXT, ' +
                       'is_masternode INT, ' +
                       'UNIQUE(node_address, timestamp) ON CONFLICT IGNORE)')

    if CONF.has_key('dash_insight_api'):
        dash_masternodes = get_dash_masternode_addresses()
        is_dash = True
    else:
        dash_masternodes = None
        is_dash = False

    insert_nodes = []
    for node in nodes:
        row = get_row(node)
        address = "{}:{}".format(row[0], row[1])
        is_masternode = address in dash_masternodes if is_dash else None
        insert_nodes.append([timestamp, row[6], address, row[2], row[3], row[9],
                             row[10], row[13], row[15], is_masternode])

    connection.executemany('INSERT INTO ' + CONF['coin_name'] + '_nodes (' +
                           'timestamp, last_block, node_address, protocol_version, ' +
                           'client_version, country_iso, country_name, city, ' +
                           'isp_cloud, is_masternode) '
                           'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', insert_nodes)
    connection.commit()
    connection.close()
    logging.info("Store took %d seconds", time.time() - start)


def calculate_node_uptime(connection, nodes, timestamp, interval_name,
                          interval_seconds, coin_name):
    """
    Calculates uptime for all ndes in the specified interval.
    """
    result = connection.cursor().execute(
        'SELECT DISTINCT timestamp ' +
        'FROM ' + coin_name + '_nodes ' +
        'WHERE timestamp >= ?',
        [timestamp - interval_seconds])
    all_scans_in_interval = []
    for row in result:
        all_scans_in_interval.append(row['timestamp'])

    encounters_per_node = connection.cursor().execute(
        'SELECT node_address, count(timestamp) AS times_encountered, min(timestamp) AS node_first_encountered ' +
        'FROM ' + coin_name + '_nodes ' +
        'WHERE timestamp >= ? ' +
        'GROUP BY node_address',
        [timestamp - interval_seconds])

    for row in encounters_per_node:
        total_scans_since_first_encounter = \
            filter(lambda i: i >= row['node_first_encountered'], all_scans_in_interval)
        percentage = row['times_encountered'] / len(list(total_scans_since_first_encounter)) * 100
        if nodes.has_key(row['node_address']):
            nodes[row['node_address']][interval_name] = '{:.2f}%'.format(percentage)


def export_coin_nodes(timestamp, config, export_dir, indicate_dash_masternodes):
    """
    Merges enumerated data for the specified nodes and exports them into
    timestamp-prefixed CSV and TXT files.
    """
    start = time.time()
    utils.create_folder_if_not_exists(export_dir)
    base_path = os.path.join(export_dir, "{}".format(timestamp))
    csv_path = base_path + ".csv"
    txt_path = base_path + ".txt"

    connection = sqlite3.connect(config['storage_file'], timeout=120)
    connection.row_factory = sqlite3.Row

    # Select all nodes that have been online at least once in the last 24 hours
    nodes_online_24h = connection.execute('SELECT * ' +
                                          'FROM ' + config['coin_name'] + '_nodes ' +
                                          'WHERE timestamp >= ?', [time.time() - 24 * 60 * 60])

    block_height_values = connection.execute('SELECT last_block ' +
                                             'FROM ' + config['coin_name'] + '_nodes ' +
                                             'WHERE timestamp = ?', [timestamp])
    block_height_values = map(lambda i: i['last_block'], block_height_values.fetchall())
    median_block_height = utils.median(block_height_values)

    # Turn nodes into a dict of node_address -> data
    nodes_online_24h_dict = {}
    for row in nodes_online_24h:
        nodes_online_24h_dict[row['node_address']] = dict(itertools.izip(row.keys(), row))

    for (interval_name, interval_seconds) in UPTIME_INTERVALS.items():
        calculate_node_uptime(connection, nodes_online_24h_dict, timestamp,
                              interval_name, interval_seconds, config['coin_name'])

    with open(csv_path, 'a') as csv_file, open(txt_path, 'a') as txt_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
        txt_writer = csv.writer(txt_file, delimiter=" ", quoting=csv.QUOTE_NONNUMERIC, encoding='utf-8')
        for node in nodes_online_24h_dict.values():
            output_data = [
                node['node_address'],
                node.get('uptime_two_hours', '100.00%'),
                node.get('uptime_eight_hours', '100.00%'),
                node.get('uptime_day', '100.00%'),
                node.get('uptime_seven_days', '100.00%'),
                node.get('uptime_thirty_days', '100.00%'),
                node['last_block'],
                node['protocol_version'],
                node['client_version'],
                node['country_iso'],
                node['country_name'],
                node['city'],
                node['isp_cloud']]

            is_synced = abs(median_block_height - node['last_block']) <= \
                        config['max_block_height_difference']
            output_data.append(1 if is_synced else 0)

            if indicate_dash_masternodes and node['is_masternode'] is not None:
                output_data.append(node['is_masternode'])

            if is_synced or config['include_out_of_sync']:
                csv_writer.writerow(output_data)
                txt_writer.writerow(output_data)

    connection.close()
    logging.info("Export took %d seconds", time.time() - start)
    logging.info("Wrote %s and %s", csv_path, txt_path)


def export_all_nodes(timestamp, meta_conf):
    conf = ConfigParser()
    conf.read(meta_conf)
    all_coins = conf.get('meta', 'enabled_coins').strip().split(',')
    for coin in all_coins:
        if REDIS_CONN.get(coin + '_crawls') == 0:
            return

    for coin in all_coins:
        REDIS_CONN.set(coin + 'crawls', 0)

    for c in conf.get('meta', 'config_files').strip().split(","):
        coin_conf = utils.parse_config(c, 'export')
        export_coin_nodes(timestamp, coin_conf, conf.get('meta', 'export_all_dir'),
                          False)


def main(argv):
    if len(argv) < 3 or not os.path.exists(argv[2]):
        print("Usage: export.py [coin.conf] [meta.conf]")
        return 1

    CONF.update(utils.parse_config(argv[1], 'export'))

    # Initialize logger
    loglevel = logging.INFO
    if CONF['debug']:
        loglevel = logging.DEBUG

    logformat = ("%(asctime)s %(levelname)s (%(funcName)s) "
                 "%(message)s")
    logging.basicConfig(level=loglevel,
                        format=logformat,
                        filename=CONF['logfile'],
                        filemode='w')

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
            REDIS_CONN.incr(CONF['coin_name'] + '_crawls', 1)
            timestamp = int(msg['data'])  # From ping.py's 'snapshot' message
            logging.info("Timestamp: %d", timestamp)
            nodes = REDIS_CONN.smembers('opendata')
            logging.info("Nodes: %d", len(nodes))
            store_reachable_nodes(nodes, timestamp)
            export_coin_nodes(timestamp, CONF, CONF['export_dir'], True)
            export_all_nodes(timestamp, argv[2])
            REDIS_CONN.publish(publish_key, timestamp)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
