#!/bin/bash
# --- bitcoin mainnet: f9beb4d9 (db = 0) ---
python -u crawl.py conf/bitcoin/crawl.conf master > log/crawl.f9beb4d9.master.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/crawl.f9beb4d9.slave.1.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/crawl.f9beb4d9.slave.2.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/crawl.f9beb4d9.slave.3.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/crawl.f9beb4d9.slave.4.out 2>&1 &
python -u crawl.py conf/bitcoin/crawl.conf slave > log/crawl.f9beb4d9.slave.5.out 2>&1 &

python -u ping.py conf/bitcoin/ping.conf master > log/ping.f9beb4d9.master.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.1.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.2.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.3.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.4.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.5.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.6.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.7.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.8.out 2>&1 &
python -u ping.py conf/bitcoin/ping.conf slave > log/ping.f9beb4d9.slave.9.out 2>&1 &

python -u resolve.py conf/bitcoin/resolve.conf > log/resolve.f9beb4d9.out 2>&1 &

python -u export.py conf/bitcoin/export.conf > log/export.f9beb4d9.out 2>&1 &

python -u seeder.py conf/bitcoin/seeder.conf > log/seeder.f9beb4d9.out 2>&1 &

python -u pcap.py conf/bitcoin/pcap.conf > log/pcap.f9beb4d9.1.out 2>&1 &
python -u pcap.py conf/bitcoin/pcap.conf > log/pcap.f9beb4d9.2.out 2>&1 &
python -u pcap.py conf/bitcoin/pcap.conf > log/pcap.f9beb4d9.3.out 2>&1 &
