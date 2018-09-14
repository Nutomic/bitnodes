#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess

message = 'This will kill all running python2 processes (even those not started by coincrawler. Continue?'
reply = str(raw_input(message + ' (y/N): ')).lower().strip()
if len(reply) > 0 and reply[0] == 'y':
    subprocess.call(['killall', 'python2'])
else:
    print 'Doing nothing.'