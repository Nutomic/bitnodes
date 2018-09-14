#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from ConfigParser import ConfigParser
import subprocess

conf = ConfigParser()
conf.read('conf/meta.conf')

coins = conf.get('meta', 'enabled_coins').strip().split(',')

for coin in coins:
    subprocess.call(['./start-coin.py', coin])
