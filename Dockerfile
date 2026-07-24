FROM node:20-alpine AS frontend_build

WORKDIR /app
COPY package.json webpack.config.js ./
RUN npm install && npm install webpack

COPY ./assets ./assets
RUN npm run build


FROM python:3.12-slim-bookworm


ENV IMAGE_VERSION=0.6
ARG IMAGE_VERSION=${IMAGE_VERSION}

LABEL project='dis'
LABEL version='${IMAGE_VERSION}-web'

ENV LANG=en_US.UTF-8
ENV TZ=Europe/Moscow
ENV PYTHONPATH="${PYTHONPATH}:/usr/src/project/app"

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /usr/src/project

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir

ADD ./scripts/local_start.sh ./scripts/
ADD ./db_versioning ./db_versioning/
ADD ./app ./app/
COPY --from=frontend_build /app/src ./src/

CMD ["./scripts/local_start.sh"]
