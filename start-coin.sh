#!/bin/bash
set -e

coin="$1"
if [ "$coin" != "bitcoin" ] && [ "$coin" != "bitcoincash" ] &&
        [ "$coin" != "dash" ] && [ "$coin" != "litecoin" ]; then
    echo "Usage: ./start-coin bitcoin|bitcoincash|dash|litecoin";
    exit;
fi

mkdir -p "log/$coin/"
python2 -u src/crawl.py "conf/$coin.conf" master > "log/$coin/crawl.master.out" 2>&1 &
python2 -u src/crawl.py "conf/$coin.conf" slave > "log/$coin/crawl.slave.1.out" 2>&1 &
python2 -u src/crawl.py "conf/$coin.conf" slave > "log/$coin/crawl.slave.2.out" 2>&1 &

python2 -u src/ping.py "conf/$coin.conf" master > "log/$coin/ping.master.out" 2>&1 &
python2 -u src/ping.py "conf/$coin.conf" slave > "log/$coin/ping.slave.1.out" 2>&1 &
python2 -u src/ping.py "conf/$coin.conf" slave > "log/$coin/ping.slave.2.out" 2>&1 &
python2 -u src/ping.py "conf/$coin.conf" slave > "log/$coin/ping.slave.3.out" 2>&1 &
python2 -u src/ping.py "conf/$coin.conf" slave > "log/$coin/ping.slave.4.out" 2>&1 &

python2 -u src/resolve.py "conf/$coin.conf" > "log/$coin/resolve.out" 2>&1 &

python2 -u src/export.py "conf/$coin.conf" > "log/$coin/export.out" 2>&1 &
