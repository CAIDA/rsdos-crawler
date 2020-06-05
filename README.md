# RSDoS Crawler

> Crawler for Targets of RSDoS Attacks

Its purpose is to crawl targets of Randomly and Uniformly Spoofed Denial-of-Service attacks (RSDoS attacks) observed at
the UCSD Network Telescope. The crawler is given the IP addresses of targets. From this the crawler returns the 
responses of all succeeded requests. 


## Table of Contents

- **[Features](#features)**
- **[Requirements](#requirements)**
- **[Installation](#installation)**
- **[Quick Start](#quick-start)**
- **[Deployment](#deployment)**
- **[Documentation](#documentation)**
- **[References](#references)**


## Features

- **Stream attacks**: The attacks are streamed as attack vectors from the UCSD Telescope DDoS Metadata. 
:warning: **In development!**
- **Track attacks**: The streamed attack vectors are tracked with reference to unique attacks, on a particular target
and at a particular starting time. 
:warning: **In development!**
- **Resolve hosts**: The IP addresses of the attacked targets are resolved to their host names with a naive reverse DNS
resolution. The already resolved host names are cached. 
:warning: **In development!**
- **Crawl hosts**: The resolved host names are crawled in various ways. First, they are crawled as soon as the attack is
reported. If hosts do not respond, the crawl is retried multiple times. Then, the hosts are periodically recrawled for a 
certain period of time. This process is done cautiously so that hosts are not crawled multiple times in a certain period 
of time. 
:warning: **In development!** 
- **Write records**: The records of all completed attacks are written in WARC files. When an attack is not ongoing 
anymore, and its crawls are completed, all its records including the attack vectors, resolved host names and crawls are 
written. 
:warning: **In development!**


## Requirements

- **Java**: Make sure that you have Java installed in version 8 or higher.
- **GCC**: We also depend on a newer gcc/clang with C++11 support.
- **Python**: You will also need a current version of Python, but at least Python 3.6.


## Installation

### Apache Kafka

```bash
# download kafka (check newer version)
wget https://downloads.apache.org/kafka/2.5.0/kafka_2.12-2.5.0.tgz

# extract kafka
tar xzf kafka_2.12-2.5.0.tgz

# move kafka 
mv kafka_2.12-2.5.0 /usr/local/kafka
```


### RocksDB

```bash
# install dependencies 
apt install libgflags-dev libsnappy-dev zlib1g-dev libbz2-dev libzstd-dev

# clone repository
git clone https://github.com/facebook/rocksdb.git

# make rocks db
cd rocksdb/
make install-shared INSTALL_PATH=/usr
```


### Virtual Environment

```bash
# create virtual environment
python3 -m venv env

# install requirements
env/bin/pip install -r requirements.txt
```


## Quick Start


## Deployment


## Documentation


## References

