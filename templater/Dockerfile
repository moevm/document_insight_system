FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3.6 python3-pip
RUN apt-get update && apt-get install -y \
    python3.6 \
    python3-pip \
    libxml2-dev \
    libxslt1-dev
RUN pip3 install --upgrade pip setuptools
RUN pip3 install --prefer-binary markupsafe==2.0.1
# RUN apt-get install -y pandoc

COPY requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

COPY app /app

ENV PYTHONPATH=/app
WORKDIR /app

RUN cd /usr/local/lib/python3.6/dist-packages && \
    python3 /app/setup.py develop
