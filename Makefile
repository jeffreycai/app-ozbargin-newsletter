## load and export .env
ifneq (,$(wildcard ./.env))
	include .env
	export
endif

## shorthand of docker-compose run prefix command
RUN=DOCKER_IMAGE_NAME=$(DOCKER_IMAGE_NAME) docker-compose run --rm --workdir /opt/app/app worker

init:
	python3 -m pip install -r app/requirements.txt
.PHONY: init

run: up init scrape_home

scrape_home: up
	python3 app/scrape_home.py
.PHONY: run

scrape_nodes: up
	python3 app/scrape_nodes.py
.PHONY: run

up:
	docker-compose ps -q | grep -q . || (docker-compose up -d && sleep 5)
.PHONY: up

down:
	docker-compose stop
	docker-compose rm -f
.PHONY: down

translate_nodes: up
	python3 app/translate_nodes.py
.PHONY: translate_nodes

draw: up
	cd app && python3 draw.py
.PHONY: draw

screenshot: up
	${RUN} /root/.nvm/versions/node/v21.5.0/bin/node screenshot.js
.PHONY: screenshot

sendmail: up
	${RUN} python3 sendmail.py
.PHONY: sendmail

cleanup:
	rm -rf app/publish/output*
	docker volume ls -q | grep ozbargin | xargs -r docker volume rm -f
.PHONY: cleanup