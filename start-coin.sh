#!/bin/bash
set -e

coin="$1"
if [ "$coin" != "bitcoin" ] && [ "$coin" != "bitcoincash" ] &&
        [ "$coin" != "dash" ] && [ "$coin" != "litecoin" ]; then
    echo "Usage: ./start-coin bitcoin|bitcoincash|dash|litecoin";
    exit;
fi

mkdir -p "log/$coin/"
python -u crawl.py "conf/$coin/crawl.conf" master > "log/$coin/crawl.master.out" 2>&1 &
python -u crawl.py "conf/$coin/crawl.conf" slave > "log/$coin/crawl.slave.1.out" 2>&1 &
python -u crawl.py "conf/$coin/crawl.conf" slave > "log/$coin/crawl.slave.2.out" 2>&1 &

python -u ping.py "conf/$coin/ping.conf" master > "log/$coin/ping.master.out" 2>&1 &
python -u ping.py "conf/$coin/ping.conf" slave > "log/$coin/ping.slave.1.out" 2>&1 &
python -u ping.py "conf/$coin/ping.conf" slave > "log/$coin/ping.slave.2.out" 2>&1 &
python -u ping.py "conf/$coin/ping.conf" slave > "log/$coin/ping.slave.3.out" 2>&1 &
python -u ping.py "conf/$coin/ping.conf" slave > "log/$coin/ping.slave.4.out" 2>&1 &

python -u resolve.py "conf/$coin/resolve.conf" > "log/$coin/resolve.out" 2>&1 &

python -u export.py "conf/$coin/export.conf" > "log/$coin/export.out" 2>&1 &

python -u seeder.py "conf/$coin/seeder.conf" > "log/$coin/seeder.out" 2>&1 &

python -u pcap.py "conf/$coin/pcap.conf" > "log/$coin/pcap.1.out" 2>&1 &
