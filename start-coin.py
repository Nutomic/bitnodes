#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import subprocess
from ConfigParser import ConfigParser
import os


def start_process(source_file, coin, arg1, out_file):
    config = 'conf/{}.conf'.format(coin)
    out_file_path = 'log/{}/{}'.format(coin, out_file)
    out_file_descriptor = open(out_file_path, 'w')
    subprocess.Popen(['python2', source_file, config, arg1],
                     stdout=out_file_descriptor, stderr=subprocess.STDOUT,
                     close_fds=True)


conf = ConfigParser()
conf.read('conf/meta.conf')

coins = conf.get('meta', 'enabled_coins').strip().split(',')

if sys.argv[1] not in coins:
    print 'Usage: ./start-coin bitcoin|bitcoincash|dash|litecoin'
    exit()

coin = sys.argv[1]

log_folder = 'log/{}'.format(coin)
if not os.path.exists(log_folder):
    os.makedirs(log_folder)

start_process('./src/crawl.py', coin, 'master', 'crawl.master.out')
start_process('./src/crawl.py', coin, 'slave', 'crawl.slave.1.out')
start_process('./src/crawl.py', coin, 'slave', 'crawl.slave.2.out')

start_process('./src/ping.py', coin, 'master', 'crawl.master.out')
start_process('./src/ping.py', coin, 'slave', 'crawl.slave.1.out')
start_process('./src/ping.py', coin, 'slave', 'crawl.slave.2.out')
start_process('./src/ping.py', coin, 'slave', 'crawl.slave.3.out')

start_process('./src/resolve.py', coin, str(None), 'resolve.out')

start_process('./src/export.py', coin, 'conf/meta.conf', 'export.out')
