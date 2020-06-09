# RSDoS Crawler

> Crawler for Targets of RSDoS Attacks

Its purpose is to crawl targets of Randomly and Uniformly Spoofed Denial-of-Service attacks (RSDoS attacks) observed at
the UCSD Network Telescope. The crawler streams the observed attacks there, organizes them into distinct targets by 
the IP addresses and start times. Then it tries to crawl these targets, or rather their hosts, and records the responses
send by them.


## Table of Contents

- **[Features](#features)**
- **[Requirements](#requirements)**
- **[Installation](#installation)**
- **[Quick Start](#quick-start)**
- **[Deployment](#deployment)**
- **[Documentation](#documentation)**
- **[References](#references)**


## Features

- **Stream attacks**: The RSDoS attacks are streamed from the UCSD Telescope DDoS Metadata. This data is periodically 
written in objects in a Swift container. In these objects are recorded the observed attack vectors in the respective 
time period. The RSDoS Crawler relies on these vectors to identify targets of attacks. 
:warning: **In development!**
- **Track targets**: For one and the same attack, on a specific IP address at a specific start time, usually there are 
recorded many attack vectors over time. To track an attack over its entire duration, these vectors are considered 
dependently. In this way, the target of an attack may be crawled over an extended period of time. And the results of the 
RSDoS Crawler are neatly collected for each distinct target. 
:warning: **In development!**
- **Resolve hosts**: The IP addresses of the attacked targets are resolved to their host names with a naive reverse DNS
resolution. The already resolved host names are cached. 
:warning: **In development!**
- **Crawl hosts**: The host names resolved from the targets are crawled in various ways. First, they are crawled as soon 
as the attack is reported. Second, if hosts do not respond, then the crawl is tried again and again with a certain delay 
until a maximum number of retries is exceeded. Third, all host names from the target are periodically recrawled with a 
longer delay possibly beyond the duration of the attack. This process is done cautiously so that hosts are not crawled 
multiple times in a certain period of time. 
:warning: **In development!** 
- **Write records**: After each crawl, the request to and the response from the host of the target are recorded in a 
WARC record together with the target. These records are written periodically. 
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

```bash
# use development settings
export SIMPLE_SETTINGS=doscrawler.settings.development

# start worker
faust -A doscrawler.app worker -l info
```


## Deployment


## Documentation


## References

