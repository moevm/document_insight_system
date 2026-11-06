FROM node:20-alpine AS frontend_build

WORKDIR /app
COPY package.json package-lock.json webpack.config.js ./
RUN npm ci --include=dev --no-audit --no-fund

COPY ./assets ./assets
RUN npm run build


FROM python:3.12-slim-bookworm

ARG IMAGE_VERSION


ENV LANG=en_US.UTF-8 \
    TZ=Europe/Moscow \
    PYTHONPATH="/usr/src/project/app" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends locales tzdata \
    && sed -i '/^# en_US.UTF-8 UTF-8/s/^# //' /etc/locale.gen \
    && locale-gen en_US.UTF-8 \
    && rm -rf /var/lib/apt/lists/*

RUN ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime \
    && echo "${TZ}" > /etc/timezone

WORKDIR /usr/src/project

COPY requirements.lock .
RUN python3 -m pip install --require-hashes -r requirements.lock --no-cache-dir

# The same numeric identity owns shared uploads in both images.
RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app \
    && install -d -o app -g app /usr/src/project/files

# Script entrypoints need the package root as well as legacy top-level imports.
ENV HOME=/home/app \
    PYTHONPATH="/usr/src/project:/usr/src/project/app"

COPY scripts/local_start.sh scripts/init_volumes.sh ./scripts/
COPY db_versioning ./db_versioning/
COPY app ./app/
COPY --from=frontend_build /app/src ./src/

ARG VCS_REF=unknown
ARG BUILD_DATE=unknown
ARG SOURCE_BRANCH=unknown
ARG SOURCE_STATE=unknown

LABEL project="dis" \
    version="${IMAGE_VERSION}" \
    org.opencontainers.image.version="${IMAGE_VERSION}" \
    org.opencontainers.image.revision="${VCS_REF}" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.source="https://github.com/moevm/document_insight_system" \
    org.opencontainers.image.source-state="${SOURCE_STATE}" \
    dis.role="web"

ENV APP_VERSION="${IMAGE_VERSION}" \
    APP_COMMIT="${VCS_REF}" \
    APP_BUILD_DATE="${BUILD_DATE}" \
    APP_BRANCH="${SOURCE_BRANCH}" \
    APP_SOURCE_STATE="${SOURCE_STATE}"

USER app:app

CMD ["./scripts/local_start.sh"]
