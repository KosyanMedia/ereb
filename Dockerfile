FROM centos:7
MAINTAINER Dmitry Kuzmenkov <dmitry@wagh.ru>

ARG USER_ID=1000

RUN useradd -u $USER_ID box && \
  yum -y install glibc-common && \
  localedef -i en_US -f UTF-8 en_US.UTF-8 && \
  yum -y install gcc gcc-c++ make zlib zlib-devel openssl openssl-devel \
  libxml2 libxml2-devel libxslt libxslt-devel sqlite3 sqlite-devel file && \
  yum -y clean all && \
  { for i in /var/lib/yum/yumdb/*/*/* ; do mv $i $i.old ; cat $i.old > $i ; rm -f $i.old ; done }

ENV LANGUAGE=en_US:en \
  LANG=en_US.UTF-8 \
  LC_ALL=en_US.UTF-8 \
  PYTHONPATH=/home/box/yasen \
  PYTHONIOENCODING=UTF-8

RUN curl -sS https://www.python.org/ftp/python/3.5.1/Python-3.5.1.tgz > python.tgz && \
  gunzip python.tgz && tar xf python.tar && \
  cd Python-3.5.1 && ./configure --prefix=/usr && make -j4 && make install && ldconfig && cd .. && \
  rm -fr Python-3.5.1 && rm -f python.tar

RUN curl -sS https://bootstrap.pypa.io/get-pip.py > get-pip.py && \
  python3 get-pip.py && rm -f get-pip.py && pip3 install --upgrade pip && \
  mkdir /home/box/ereb

COPY requirements.txt /home/box/ereb/requirements.txt
RUN pip3 install --no-cache-dir --src /home/box/pip_src -r /home/box/ereb/requirements.txt

COPY . /home/box/ereb
WORKDIR /home/box/ereb
RUN chown -hR box:box /home/box
USER box
STOPSIGNAL SIGTERM
EXPOSE 8888
ENTRYPOINT ["python3", "ereb.py"]
