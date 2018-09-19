#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
start_coin = __import__("start-coin")

conf = ConfigParser()
conf.read('conf/meta.conf')

coins = conf.get('meta', 'enabled_coins').strip().split(',')

for coin in coins:
    start_coin.main(coin)
