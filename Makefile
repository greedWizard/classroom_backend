DC=docker-compose
STORAGES=docker-compose/storage.yml
DEVFILE=docker-compose.yaml
PRODFILE=docker-compose.prod.yaml


.PHONY: network
network:
	docker network create classroom-network

.PHONY: prod
prod:
	${DC} -f ${PRODFILE} up --build -d

.PHONY: dev
dev:
	${DC} -f ${DEVFILE} up --build -d

.PHONY: dev-logs
dev-logs:
	${DC} -f ${DEVFILE} logs

.PHONY: prod-logs
prod-logs:
	${DC} -f ${PRODFILE} logs

.PHONY: stop-prod
stop-prod:
	${DC} -f ${PRODFILE} stop

.PHONY: stop-dev
stop-dev:
	${DC} -f ${DEVFILE} down