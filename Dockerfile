FROM ubuntu:20.04
ENV LANG en_US.UTF-8

WORKDIR /usr/src/project

RUN apt update && apt install -y software-properties-common curl gnupg python3-pip python3.8-dev
RUN curl -sL https://deb.nodesource.com/setup_16.x  | bash -
RUN apt install -y nodejs libreoffice

ADD package.json webpack.config.js requirements.txt /usr/src/project/

RUN npm install && npm audit fix && npm install webpack
RUN python3.8 -m pip install -r requirements.txt

ADD ./assets /usr/src/project/assets
ADD ./scripts/local_start.sh /usr/src/project/scripts/
RUN npm run build

ADD ./app /usr/src/project/app/
ADD ./db_versioning /usr/src/project/db_versioning/

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project"

CMD ./scripts/local_start.sh
