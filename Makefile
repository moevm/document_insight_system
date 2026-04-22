include .env

VERSION=${IMAGE_VERSION}
WORKER_BASE_IMAGE=dvivanov/dis:worker-base-${VERSION}
WORKER_BASE_DOCKERFILE=Dockerfile_worker_base
BUILD_ARG_STR=--build-arg IMAGE_VERSION=${VERSION}

define image_exists
$(shell docker image inspect $(1) > /dev/null 2>&1 && echo "yes")
endef


.PHONY: build-base build-web build-worker build-tests check-base build build-all up upd full-up full-up-d down tests

build-base: $(WORKER_BASE_DOCKERFILE)
	docker build -t $(WORKER_BASE_IMAGE) ${BUILD_ARG_STR} -f $(WORKER_BASE_DOCKERFILE) . ;
	
build-web: $(WORKER_DOCKERFILE)
	docker compose build ${BUILD_ARG_STR} web ;

build-worker: $(WEB_DOCKERFILE)
	docker compose build ${BUILD_ARG_STR} worker ;

build-tests:
	docker compose -f docker-compose.yml -f docker-compose-selenium.yml build ${BUILD_ARG_STR} selenium-tests ;

check-base:
	@if [ "$(call image_exists,$(WORKER_BASE_IMAGE))" != "yes" ]; then \
		echo "Trying to pull $(WORKER_BASE_IMAGE) from remote..." ; \
		if docker pull $(WORKER_BASE_IMAGE) 2>/dev/null ; then \
			echo "Successfully pulled $(WORKER_BASE_IMAGE)" ; \
		else \
			echo "Remote image not found or cannot pull. Building locally..." ; \
			$(MAKE) build-base ; \
		fi \
	else \
		echo "${WORKER_BASE_IMAGE} already exists"; \
	fi

build: build-web build-worker

build-all: build-base build

up:
	docker compose -f docker-compose.yml up ;

up-d:
	docker compose -f docker-compose.yml up -d ;

full-up:
	docker compose -f docker-compose.yml -f lt_docker/docker-compose.yaml up ;

full-up-d:
	docker compose -f docker-compose.yml -f lt_docker/docker-compose.yaml up -d ;

down:
	docker compose -f docker-compose.yml -f lt_docker/docker-compose.yaml down ;

tests: build-all build-tests
	docker compose -f docker-compose.yml -f lt_docker/docker-compose.yaml -f docker-compose-selenium.yml up -d
