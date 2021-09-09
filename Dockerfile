FROM ubuntu:20.04
ENV LANG en_US.UTF-8

RUN apt update
RUN apt-get install -y software-properties-common
RUN apt install -y curl gnupg
RUN apt install -y python3-pip python3.8-dev
RUN curl -sL https://deb.nodesource.com/setup_16.x  | bash -
RUN apt install -y  nodejs
RUN add-apt-repository ppa:libreoffice/ppa
RUN apt install -y unoconv

ADD . /usr/src/project
WORKDIR /usr/src/project

RUN npm install
RUN npm audit fix
RUN npm install webpack

RUN  python3.8 -m pip install -r dependencies.txt
ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project"

RUN ./act.sh -b
CMD ./scripts/local_start.sh
