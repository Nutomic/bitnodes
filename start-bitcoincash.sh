#!/bin/bash
set -e

mkdir -p log/bitcoincash/
python -u crawl.py conf/bitcoincash/crawl.conf master > log/bitcoincash/crawl.master.out 2>&1 &
python -u crawl.py conf/bitcoincash/crawl.conf slave > log/bitcoincash/crawl.slave.1.out 2>&1 &
python -u crawl.py conf/bitcoincash/crawl.conf slave > log/bitcoincash/crawl.slave.2.out 2>&1 &

python -u ping.py conf/bitcoincash/ping.conf master > log/bitcoincash/ping.master.out 2>&1 &
python -u ping.py conf/bitcoincash/ping.conf slave > log/bitcoincash/ping.slave.1.out 2>&1 &
python -u ping.py conf/bitcoincash/ping.conf slave > log/bitcoincash/ping.slave.2.out 2>&1 &
python -u ping.py conf/bitcoincash/ping.conf slave > log/bitcoincash/ping.slave.3.out 2>&1 &
python -u ping.py conf/bitcoincash/ping.conf slave > log/bitcoincash/ping.slave.4.out 2>&1 &

python -u resolve.py conf/bitcoincash/resolve.conf > log/bitcoincash/resolve.out 2>&1 &

python -u export.py conf/bitcoincash/export.conf > log/bitcoincash/export.out 2>&1 &

python -u seeder.py conf/bitcoincash/seeder.conf > log/bitcoincash/seeder.out 2>&1 &

python -u pcap.py conf/bitcoincash/pcap.conf > log/bitcoincash/pcap.1.out 2>&1 &
