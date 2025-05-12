FROM node:20-alpine as frontend_build

WORKDIR /app
ADD package.json webpack.config.js ./
RUN npm install && npm install webpack

ADD ./assets ./assets
RUN npm run build

FROM dvivanov/dis-base:v0.4

LABEL project='dis'
LABEL version='0.4'

WORKDIR /usr/src/project

ADD ./scripts/local_start.sh ./scripts/
ADD ./db_versioning ./db_versioning/
ADD ./app ./app/
COPY --from=frontend_build /app/src ./src/

ENV PYTHONPATH "${PYTHONPATH}:/usr/src/project/app"

RUN apt update && apt install -y texlive-latex-base \
    texlive-fonts-recommended \
    texlive-lang-cyrillic \
    texlive-xetex \
    latexmk \
    biber

CMD ./scripts/local_start.sh
