#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
from os.path import isfile
from shutil import copyfile


start_coin = __import__("start-coin")
meta_conf_file = 'conf/meta.conf'

if not isfile(meta_conf_file):
    copyfile('conf/meta.conf.default', meta_conf_file)

meta_conf = ConfigParser()
meta_conf.read('conf/meta.conf')

coins = meta_conf.get('meta', 'enabled_coins').strip().split(',')

for coin in coins:
    start_coin.main(coin)
