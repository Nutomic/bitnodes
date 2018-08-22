#!/bin/bash
# --- bitcoin mainnet: f9beb4d9 (db = 0) ---
mkdir -p log/bitcoin/
python -u crawl.py conf/bitcoin/crawl.conf master > log/bitcoin/crawl.master.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/bitcoin/crawl.slave.1.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/bitcoin/crawl.slave.2.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/bitcoin/crawl.slave.3.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/bitcoin/crawl.slave.4.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/bitcoin/crawl.slave.5.out 2>&1 &

python -u ping.py conf/bitcoin/ping.conf master > log/bitcoin/ping.master.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.1.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.2.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.3.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.4.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.5.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.6.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.7.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.8.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/bitcoin/ping.slave.9.out 2>&1 &

python -u resolve.py conf/bitcoin/resolve.conf > log/bitcoin/resolve.out 2>&1 &

python -u export.py conf/bitcoin/export.conf > log/bitcoin/export.out 2>&1 &

python -u seeder.py conf/bitcoin/seeder.conf > log/bitcoin/seeder.out 2>&1 &

python -u pcap.py conf/bitcoin/pcap.conf > log/bitcoin/pcap.1.out 2>&1 &
python -u pcap.py conf/bitcoin/pcap.conf > log/bitcoin/pcap.2.out 2>&1 &
python -u pcap.py conf/bitcoin/pcap.conf > log/bitcoin/pcap.3.out 2>&1 &
