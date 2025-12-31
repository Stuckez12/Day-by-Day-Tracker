start:
	docker compose -f docker-compose.yaml up -d

stop:
	docker compose -f docker-compose.yaml stop

build:
	docker compose -f docker-compose.yaml build

remove:
	docker compose -f docker-compose.yaml down

logs:
	docker compose -f docker-compose.yaml logs -f

restart:
	$(MAKE) stop
	$(MAKE) start

full-restart:
	$(MAKE) stop
	$(MAKE) build
	$(MAKE) start


upgrade-db:
	@docker-compose -f docker-compose.yaml exec api alembic -c /api/alembic.ini upgrade head

VERSION ?= -1
downgrade-db:
	@echo "Downgrading to/by $(VERSION) version"
	@docker-compose -f docker-compose.yaml exec api alembic -c /api/alembic.ini downgrade $(VERSION)

auto-revision-db:
ifndef MESSAGE
	$(error 'MESSAGE is not set. Usage: make auto-revision-db MESSAGE="message"')
endif
	@docker-compose -f docker-compose.yaml exec api alembic -c /api/alembic.ini revision --autogenerate -m "$(MESSAGE)"
