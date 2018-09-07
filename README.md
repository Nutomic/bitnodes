Coincrawler
===========

Coincrawler is a network crawler for multiple Bitcoin-based cryptocurrencies.
At the moment, it includes configurations for Bitcoin, Bitcoin Cash, Dash
and Litecoin. The project is forked from
[Bitnodes](https://github.com/ayeowch/bitnodes).

See the [installation instructions](INSTALL.md) for steps on setting up a
machine to run Coincrawler. The
[Redis Data](https://github.com/ayeowch/bitnodes/wiki/Redis-Data) contains
the list of keys and their associated values that are written by the scripts
in this project.

If the program output takes up too much space after some time, you can safely
delete the following folders, after stopping the crawler:
```
data/crawl/
data/export/
```

License
-------

The project is licensed under the [MIT license](LICENSE).
