FROM ubuntu:18.04
ENV LANG en_US.UTF-8

RUN apt update
RUN apt -y install curl gnupg
RUN apt install -y python3-pip python3.8-dev
RUN curl -sL https://deb.nodesource.com/setup_10.x  | bash -
RUN apt -y install nodejs   

ADD . /usr/src/project
WORKDIR /usr/src/project

RUN npm install
RUN npm install webpack

RUN  python3.8 -m pip install -r dependencies.txt
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project"

RUN ./act.sh -b
CMD python3.8 ./app/server.py -p
