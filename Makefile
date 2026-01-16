start:
	@docker compose -f docker-compose.dev.yaml up -d

stop:
	@docker compose -f docker-compose.dev.yaml stop

build:
	@docker compose -f docker-compose.dev.yaml build

build-no-cache:
	@docker compose -f docker-compose.dev.yaml build --no-cache

remove:
	@docker compose -f docker-compose.dev.yaml down

logs:
	@docker compose -f docker-compose.dev.yaml logs -f

restart:
	$(MAKE) stop
	$(MAKE) start

full-restart:
	$(MAKE) stop
	$(MAKE) build
	$(MAKE) start

hard-restart:
	$(MAKE) stop
	$(MAKE) build-no-cache
	$(MAKE) start


################################################################################
# Database
################################################################################


upgrade-db:
	@docker-compose -f docker-compose.dev.yaml exec api alembic -c /api/alembic.ini upgrade head

VERSION ?= -1
downgrade-db:
	@echo "Downgrading to/by $(VERSION) version"
	@docker-compose -f docker-compose.dev.yaml exec api alembic -c /api/alembic.ini downgrade $(VERSION)

auto-revision-db:
ifndef MESSAGE
	$(error 'MESSAGE is not set. Usage: make auto-revision-db MESSAGE="message"')
endif
	@docker-compose -f docker-compose.dev.yaml exec api alembic -c /api/alembic.ini revision --autogenerate -m "$(MESSAGE)"


################################################################################
# Frontend
################################################################################


npm-install:
	@cd frontend && npm i $@


################################################################################
# Production
################################################################################


start-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d

stop-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod stop

remove-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod down
