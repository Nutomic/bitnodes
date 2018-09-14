#### Launch Server

Required specifications:
- high bandwidth and low latency
- at least 8 GB of RAM (plus swap)
- at least 4 CPU cores

For security reasons, it is recommended that you use a seperate user account
and disable root login for ssh. You should also disable password-based login
and use a key pair instead.

#### Configure Locales

    # dpkg-reconfigure locales
        en_US.UTF-8 UTF-8
        en_US.UTF-8

    # vi /etc/environment
        LC_CTYPE=en_US.UTF-8

#### Configure Timezone

    # dpkg-reconfigure tzdata
        None of the above
        UTC

#### Update Packages and Install Packages

    # apt-get update
    # apt-get upgrade
    # apt-get install build-essential python-dev python-pip python-setuptools tor git killall

#### Adjust various config files

    # nano /etc/sysctl.conf
        net.ipv4.conf.default.rp_filter=1
        net.ipv4.conf.all.rp_filter=1
        net.ipv4.tcp_syncookies=1
        net.ipv4.conf.all.accept_redirects=0
        net.ipv6.conf.all.accept_redirects=0
        net.ipv4.conf.all.send_redirects=0
        net.ipv4.conf.all.accept_source_route=0
        net.ipv6.conf.all.accept_source_route=0
        net.ipv4.conf.all.log_martians=1
        net.core.rmem_default=33554432
        net.core.wmem_default=33554432
        net.core.rmem_max=33554432
        net.core.wmem_max=33554432
        net.core.optmem_max=33554432
        net.ipv4.tcp_rmem=10240 87380 33554432
        net.ipv4.tcp_wmem=10240 87380 33554432
        net.ipv4.ip_local_port_range=2000 65500
        net.core.netdev_max_backlog=100000
        net.ipv4.tcp_max_syn_backlog=80000
        net.ipv4.tcp_max_tw_buckets=2000000
        net.ipv4.tcp_tw_reuse=1
        net.ipv4.tcp_fin_timeout=5
        net.ipv4.tcp_slow_start_after_idle=0
        net.core.somaxconn=60000
        fs.file-max=1000000
        vm.swappiness=10
        vm.min_free_kbytes=1048576
        vm.overcommit_memory=1

    # nano /etc/security/limits.conf
        * soft nofile 1000000
        * hard nofile 1000000
        # If you are running as root, you need to specify this explicitly
        root soft nofile 1000000

    # /etc/rc.local
        echo never > /sys/kernel/mm/transparent_hugepage/enabled
        echo never > /sys/kernel/mm/transparent_hugepage/defrag
        /sbin/ifconfig eth0 txqueuelen 5000

Ready, now restart the server

    # reboot now

#### Install Redis

    # apt-get install redis-server
    # nano /etc/redis/redis.conf
        unixsocket /var/run/redis/redis.sock
        unixsocketperm 777
        maxclients 50000
        # 12 GB, adjust according to your RAM size.
        maxmemory 8589934592
        maxmemory-policy volatile-ttl
        notify-keyspace-events K$z
        activerehashing no
        client-output-buffer-limit slave 512mb 256mb 300
        client-output-buffer-limit pubsub 512mb 256mb 300
        hz 20

#### Install Dash Full Node

    # apt-get install python git unzip pv
    # git clone https://github.com/moocowmoo/dashman
    # ./dashman/dashman install

Then wait until `./.dashcore/dash-cli mnsync status` shows "MASTERNODE_SYNC_FINISHED".
Depending on your hardware and internet connection, this will take roughly 30 minutes.

#### Reboot Server

    # reboot

#### Launch Crawler

    git clone https://github.com/Nutomic/coincrawler.git
    cd coincrawler/
    pip install -r requirements.txt
    ./geoip/update.sh
    ./start-all.py
