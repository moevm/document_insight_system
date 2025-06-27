FROM node:20-alpine as frontend_build

WORKDIR /app
ADD package.json webpack.config.js ./
RUN npm install && npm install webpack

ADD ./assets ./assets
RUN npm run build

FROM dvivanov/dis-base:v0.5

LABEL project='dis'
LABEL version='0.5'

WORKDIR /usr/src/project

ADD ./scripts/local_start.sh ./scripts/
ADD ./db_versioning ./db_versioning/
ADD ./app ./app/
COPY --from=frontend_build /app/src ./src/

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project/app"

CMD ./scripts/local_start.sh
