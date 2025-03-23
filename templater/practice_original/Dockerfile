FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install -y python3 python3-pip
# RUN apt-get install -y pandoc

ADD app /app

RUN pip3 install -r app/requirements.txt

ENTRYPOINT ["python3", "/app/main.py"]