## load and export .env
ifneq (,$(wildcard ./.env))
	include .env
	export
endif

## shorthand of docker-compose run prefix command
RUN=DOCKER_IMAGE_NAME=$(DOCKER_IMAGE_NAME) docker-compose run --rm --workdir /opt/app/app worker

## ops jobs
# build work image
build:
	docker build -t ${DOCKER_IMAGE_NAME} -f docker/Dockerfile .
.PHONY: build

up: down
	docker-compose up -d
.PHONY: up

down:
	docker-compose stop
	docker-compose rm -f
.PHONY: down

# debug worker container
debug: up
	sleep 2
	docker-compose exec -it worker /usr/bin/bash
	$(MAKE) -C . down
.PHONY: debug

# push work image
push:
	docker push ${DOCKER_IMAGE_NAME}
.PHONY: push

## projects
run: init scrape_home scrape_nodes translate_nodes
.PHONY: run

scrape_home: init
	${RUN} python3 scrape_home.py
.PHONY: scrape_home

scrape_nodes:
	${RUN} python3 scrape_nodes.py
.PHONY: scrape_nodes

translate_nodes:
	${RUN} python3 translate_nodes.py
.PHONY: translate_nodes

init:
	${RUN} python3 init.py
.PHONY: init

query:
	${RUN} python3 query.py
.PHONY: query

draw: # generate htmls
	${RUN} python3 draw.py
.PHONY: draw

screenshot:
	${RUN} bash -c node screenshot.js
.PHONY: screenshot

cleanup:
	rm -rf app/data/deals.db
.PHONY: cleanup