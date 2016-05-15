FROM python:latest
MAINTAINER "ezo" <ezo@kremenev.com>

ADD . /app
WORKDIR /app

ENV PATH /usr/bin:/usr/local/bin:$PATH

RUN set -x \
    && make install

CMD ["ereb"]
EXPOSE 8888
