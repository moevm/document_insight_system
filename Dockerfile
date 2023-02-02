FROM node:16-alpine as frontend_build

WORKDIR /app
ADD package.json webpack.config.js ./
RUN npm install && npm install webpack

ADD ./assets ./assets
RUN npm run build

FROM python:3.8-slim-bullseye

ENV LANG en_US.UTF-8
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/project

RUN apt update && apt install -y libreoffice-writer libreoffice-impress default-jre

ADD requirements.txt ./
RUN python3.8 -m pip install -r requirements.txt

COPY --from=frontend_build /app/src /usr/src/project/src
ADD ./scripts/local_start.sh ./scripts/
ADD ./db_versioning ./db_versioning/
ADD ./app ./app/

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project/app"

CMD ./scripts/local_start.sh
