#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
import psutil

for p in psutil.pids():
    process = psutil.Process(p)
    cmdline = process.cmdline()
    local_commands = ('./src/crawl.py', './src/ping.py', './src/resolve.py', './src/export.py')
    if len(cmdline) > 1 and cmdline[0] == 'python2' and cmdline[1] in local_commands:
        subprocess.call(['kill', str(p)])
