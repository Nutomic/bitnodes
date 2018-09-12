#### crawl.py
    [KEY]
    crawl:master:state            value = 'starting', 'running'

    node:ADDRESS-PORT-SERVICES    value = ''

    height                        value = HEIGHT (most common height)

    height:ADDRESS-PORT-SERVICES  value = HEIGHT (1 day TTL)

    elapsed                       value = ELAPSED (seconds)

    crawl:cidr:CIDR               value = NODES

    [LIST]
    nodes                         values = [(TIMESTAMP, REACHABLE_NODES), ..]

    [SET]
    pending                       values = [(ADDRESS, PORT, SERVICES), ..]

    up                            values = [node:ADDRESS-PORT-SERVICES, ..]

    [SORTED SET]
    check                         score values
                                      score = TIMESTAMP (epoch in seconds)
                                      values = [(ADDRESS, PORT, SERVICES), ..]
                                  This key is currently set by https://bitnodes.earn.com/#join-the-network

#### ping.py
    [KEY]
    bestblockhash                 value = HASH

    onion:PORT                    value = (ADDRESS, PORT) (mapping of local port to .onion node)

    ping:cidr:CIDR                value = NODES

    [LIST]
    ping:ADDRESS-PORT:NONCE       values = [TIMESTAMP, ..] (epoch for ping in milliseconds, 3 hours TTL)

    [SET]
    reachable                     values = [(ADDRESS, PORT, SERVICES, HEIGHT), ..]

    open                          values = [(ADDRESS, PORT), ..]

    opendata                      values = [(ADDRESS, PORT, VERSION, USER_AGENT, TIMESTAMP, SERVICES), ..]

    [CHANNEL]
    snapshot                      value = TIMESTAMP (epoch in seconds)

#### resolve.py
    [KEY]
    resolve:ADDRESS               field value (1 day TTL)
                                      field = 'hostname'
                                      value = HOSTNAME
                                      This key can be updated by https://bitnodes.earn.com/#join-the-network to allow e.g. A record to take precedence over PTR record

                                      field = 'geoip'
                                      value = (CITY, COUNTRY_ISO, COUNTRY_NAME, LATITUDE, LONGITUDE, TIMEZONE, ASN, ORG)

    [CHANNEL]
    resolve                       value = TIMESTAMP (epoch in seconds)

#### export.py
    [CHANNEL]
    export                        value = TIMESTAMP (epoch in seconds)

#### pcap.py
    [KEY]
    rinv:TYPE:HASH                value = TIMESTAMP (epoch in milliseconds)

    lastblockhash                 value = HASH

    [LIST]
    ping:ADDRESS-PORT:NONCE       values = [.., TIMESTAMP, ..] (epoch for pong in milliseconds, key must already exist)

    rtt:ADDRESS-PORT              values = [RTT, ..] (round-trip time in milliseconds, 3 hours TTL, max. 36 values)

    [SORTED SET]
    inv:TYPE:HASH                 score values (3 hours TTL)
                                      score = TIMESTAMP (epoch in milliseconds)
                                      values = [(ADDRESS, PORT), ..]
