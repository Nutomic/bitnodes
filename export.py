#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# export.py - Exports enumerated data for reachable nodes into CSV and TXT files
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


def get_dash_masternodes():
    url = CONF['dash_insight_api'] + '/masternodes/list'
    response = urllib.urlopen(url)
    masternodes = json.loads(response.read())
    enabled_masternodes = filter(lambda item: item['status'] == 'ENABLED', masternodes)
    return map(lambda item: item['ip'], enabled_masternodes)


def export_nodes(nodes, timestamp):
    """
    Merges enumerated data for the specified nodes and exports them into
    timestamp-prefixed CSV and TXT files.
    """
    start = time.time()
    base_path = os.path.join(CONF['export_dir'], "{}".format(timestamp))
    csv_path = base_path + ".csv"
    txt_path = base_path + ".txt"
    if CONF['dash_insight_api'] is not None:
        dash_masternodes = get_dash_masternodes()
        is_dash = True
    else:
        dash_masternodes = []
        is_dash = False

    with open(csv_path, 'a') as csv_file, open(txt_path, 'a') as txt_file:
        csv_writer = csv.writer(csv_file, delimiter=",", quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
        txt_writer = csv.writer(txt_file, delimiter=" ", quoting=csv.QUOTE_MINIMAL, encoding='utf-8')
        for node in nodes:
            row = get_row(node)
            output_data = [
                "{}:{}".format(row[0], row[1]), # IP_addr:port
                row[6],                         # last_block
                row[2],                         # protocol_version
                row[3],                         # client_version
                row[9],                         # country
                row[12],                        # city
                row[14]]                        # ISP cloud

            if is_dash:
                is_masternode = output_data[0] in dash_masternodes
                output_data.append(1 if is_masternode else 0)

            csv_writer.writerow(output_data)
            txt_writer.writerow(output_data)

    end = time.time()
    elapsed = end - start
    logging.info("Elapsed: %d", elapsed)

    logging.info("Wrote %s and %s", csv_path, txt_path)


def init_conf(argv):
    """
    Populates CONF with key-value pairs from configuration file.
    """
    conf = ConfigParser()
    conf.read(argv[1])
    CONF['logfile'] = conf.get('export', 'logfile')
    CONF['magic_number'] = unhexlify(conf.get('export', 'magic_number'))
    CONF['db'] = conf.getint('export', 'db')
    CONF['debug'] = conf.getboolean('export', 'debug')
    CONF['export_dir'] = conf.get('export', 'export_dir')
    try:
        CONF['dash_insight_api'] = conf.get('export', 'dash_insight_api')
    except NoOptionError:
        CONF['dash_insight_api'] = None

    if not os.path.exists(CONF['export_dir']):
        os.makedirs(CONF['export_dir'])


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
            export_nodes(nodes, timestamp)
            REDIS_CONN.publish(publish_key, timestamp)

    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
