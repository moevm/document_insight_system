# package.json is the only manually maintained application version.
# Ignore obsolete environment/CLI overrides so tags cannot drift from the manifest.
override IMAGE_VERSION := $(shell python3 scripts/check_versions.py --print-version)
export IMAGE_VERSION

# Build provenance is captured locally and passed explicitly to every image.
export VCS_REF ?= $(shell git rev-parse HEAD)
export BUILD_DATE ?= $(shell date -u +%Y-%m-%dT%H:%M:%SZ)
export SOURCE_BRANCH ?= $(shell git branch --show-current)
export SOURCE_STATE ?= $(shell test -z "$$(git status --porcelain)" && echo clean || echo dirty)

COMPOSE = docker compose -f docker-compose.yml
FULL_COMPOSE = $(COMPOSE) -f lt_docker/docker-compose.yaml
TEST_COMPOSE = $(FULL_COMPOSE) -f docker-compose-selenium.yml

.PHONY: sync-version check-version build-base build-web build-worker build-tests check-base build build-all up up-d full-up full-up-d down tests

build-base: sync-version Dockerfile_worker_base
	$(COMPOSE) build worker-base

build-web: sync-version Dockerfile
	$(COMPOSE) build web

build-worker: sync-version check-base Dockerfile_worker
	$(COMPOSE) build worker

build-tests: sync-version
	$(TEST_COMPOSE) build selenium-tests

sync-version:
	python3 scripts/check_versions.py --sync

check-version:
	python3 scripts/check_versions.py

check-base:
	@set -eu; \
	image=$$($(COMPOSE) --profile build-base config --images worker-base); \
	test -n "$$image"; \
	if docker image inspect "$$image" >/dev/null 2>&1; then \
		echo "$$image already exists"; \
	elif docker pull "$$image"; then \
		echo "Successfully pulled $$image"; \
	else \
		echo "Cannot pull $$image. Building locally..."; \
		$(MAKE) build-base; \
	fi

build: build-web build-worker

# A prerequisite list alone would allow base and worker to race under make -j.
build-all: build-base
	$(MAKE) build

up: sync-version
	$(COMPOSE) up

up-d: sync-version
	$(COMPOSE) up -d

full-up: sync-version
	$(FULL_COMPOSE) up

full-up-d: sync-version
	$(FULL_COMPOSE) up -d

down: sync-version
	$(FULL_COMPOSE) down

tests: build-all
	$(MAKE) build-tests
	$(TEST_COMPOSE) up -d
