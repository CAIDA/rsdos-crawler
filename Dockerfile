FROM python:3.8.4-slim

ENV APP_DIR /app
ENV WORKER_DATA_DIR /data/$WORKER_ID

RUN apt-get update -y --fix-missing \
  && apt-get install -y \
    curl \
    netcat

RUN mkdir -p $WORKER_DATA_DIR
RUN mkdir -p $APP_DIR

COPY . $APP_DIR
WORKDIR $APP_DIR

RUN pip install -r requirements.txt

ENTRYPOINT ["bash", "scripts/wait_services.sh"]

CMD ["faust", "--datadir=$WORKER_DATA_DIR", "-A", "doscrawler.app", "worker", "-l", "info"]
