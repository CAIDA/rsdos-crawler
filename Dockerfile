FROM python:3.8.4-slim

ENV HOME /root
ENV APP_HOME /app
ENV C_FORCE_ROOT=true
ENV PYTHONUNBUFFERED 1
ENV WORKER_DATA_DIRECTORY /data/$WORKER_ID

RUN apt-get update -y --fix-missing \
  && apt-get install -y \
    build-essential \
    curl \
    netcat \
    libgflags-dev \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    liblz4-dev

ENV LD_LIBRARY_PATH=/usr/local/lib \
  PORTABLE=1

RUN cd /tmp \
  && curl -sL rocksdb.tar.gz https://github.com/facebook/rocksdb/archive/v6.10.2.tar.gz > rocksdb.tar.gz \
  && tar fvxz rocksdb.tar.gz \
  && cd rocksdb-6.10.2 \
  && make shared_lib \
  && make install-shared

RUN apt-get remove -y \
  build-essential \
  curl \
  && rm -rf /tmp

RUN mkdir -p $WORKER_DATA_DIRECTORY
RUN mkdir -p $APP_HOME
COPY . $APP_HOME
WORKDIR $APP_HOME

RUN pip install -r requirements.txt

ENTRYPOINT ["bash", "scripts/wait_services.sh"]

CMD ["faust", "--datadir=$WORKER_DATA_DIRECTORY", "-A", "doscrawler.app", "worker", "-l", "info"]
