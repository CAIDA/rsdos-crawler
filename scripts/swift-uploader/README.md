# Crawl Results Uploader

Uploads crawl result GZ files to swift.

Swift container: `data-telescope-meta-dos-crawler`

```
year=2021/month=01/day=28/data-telescope-crawler-dos-202101281500.json.gz
```

## Parameters

All parameters are optional.

- `-d`, `--dir`: crawl results directory to watch, default `/home/limbo/rsdos-crawler/data/dumps`
- `-e`, `--env`: envfile path, default `/home/limbo/.stardust-creds`
- `-D`, `--delete`: whether to delete original file on upload success, default `False`

## Install

`sudo python3 setup install`

## Crontab

`crontab -e`

```
30 0 * * * /usr/local/bin/crawl-uploader --delete
```