FROM ubuntu:20.04

ENV LANG en_US.UTF-8
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/project

RUN apt update && apt install -y software-properties-common curl gnupg python3-pip python3.8-dev
RUN curl -sL https://deb.nodesource.com/setup_16.x  | bash -
RUN apt-add-repository ppa:libreoffice/ppa
RUN apt install -y nodejs libreoffice-writer-nogui libreoffice-impress-nogui

ADD package.json webpack.config.js requirements.txt ./

RUN npm install && npm audit fix && npm install webpack
RUN python3.8 -m pip install -r requirements.txt

ADD ./assets ./assets
RUN npm run build

ADD ./scripts/local_start.sh ./scripts/
ADD ./app ./app/
ADD ./db_versioning ./db_versioning/

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project/app"

CMD ./scripts/local_start.sh
