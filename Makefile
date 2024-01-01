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

up:
	docker-compose ps -q | grep -q . || (docker-compose up -d && sleep 5)
.PHONY: up

down:
	docker-compose stop
	docker-compose rm -f
.PHONY: down

# debug worker container
debug: up
	docker-compose exec -it worker /usr/bin/bash
.PHONY: debug

# push work image
push:
	docker push ${DOCKER_IMAGE_NAME}
.PHONY: push

## projects
run: up init scrape_home scrape_nodes translate_nodes draw screenshot
.PHONY: run

scrape_home: up
	${RUN} python3 scrape_home.py
.PHONY: scrape_home

scrape_nodes: up
	${RUN} python3 scrape_nodes.py
.PHONY: scrape_nodes

translate_nodes: up
	${RUN} python3 translate_nodes.py
.PHONY: translate_nodes

init: up
	${RUN} python3 init.py
.PHONY: init

draw: up # generate htmls
	${RUN} python3 draw.py
.PHONY: draw

screenshot: up
	${RUN} /root/.nvm/versions/node/v21.5.0/bin/node screenshot.js
.PHONY: screenshot

sendmail: up
	${RUN} python3 sendmail.py
.PHONY: sendmail

cleanup: #down
	rm -rf publish/output*
#	docker volume ls -q | grep ozbargin | xargs -r docker volume rm -f
.PHONY: cleanup