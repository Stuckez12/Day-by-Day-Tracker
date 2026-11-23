################################################################################
# Makefile Parameters
################################################################################

.PHONY: tests

COMPOSE_DEV =      docker compose -p dbdt-dev      -f docker-compose.dev.yaml
COMPOSE_PRE_PROD = docker compose -p dbdt-pre-prod -f docker-compose.prod.yaml
COMPOSE_PROD =     docker compose -p dbdt-prod     -f docker-compose.prod.yaml

################################################################################
# Development
################################################################################


start:
	@$(COMPOSE_DEV) up -d

stop:
	@$(COMPOSE_DEV) stop

build:
	@$(COMPOSE_DEV) build

build-no-cache:
	@$(COMPOSE_DEV) build --no-cache

remove:
	@$(COMPOSE_DEV) down --remove-orphans

destroy:
	@$(COMPOSE_DEV) down -v --remove-orphans

restart:
	$(MAKE) stop
	$(MAKE) start

rebuild:
	$(MAKE) stop
	$(MAKE) build
	$(MAKE) start

reset:
	$(MAKE) remove
	$(MAKE) build-no-cache
	$(MAKE) start

lint:
	@uv run ruff format src
	@uv run ruff check ./src
	@uv run ty check ./src


################################################################################
# Database
################################################################################


check-db:
	@$(COMPOSE_DEV) exec api alembic -c /api/alembic.ini check
	@$(COMPOSE_DEV) exec api alembic -c /api/alembic-backup.ini check

upgrade-db:
	@$(COMPOSE_DEV) exec api sh -c "alembic -c /api/alembic.ini upgrade head"

VERSION ?= -1
downgrade-db:
	@echo "Downgrading to/by $(VERSION) version"
	@$(COMPOSE_DEV) exec api alembic -c /api/alembic.ini downgrade $(VERSION)

auto-revision-db:
ifndef MESSAGE
	$(error 'MESSAGE is not set. Usage: make auto-revision-db MESSAGE="message"')
endif
	@$(COMPOSE_DEV) exec api alembic -c /api/alembic.ini revision --autogenerate -m "$(MESSAGE)"
	@$(COMPOSE_DEV) exec api chmod -R o+w src/migrations

upgrade-backup-db:
	@$(COMPOSE_DEV) exec api sh -c "alembic -c /api/alembic-backup.ini upgrade head"

VERSION ?= -1
downgrade-backup-db:
	@echo "Downgrading to/by $(VERSION) version"
	@$(COMPOSE_DEV) exec api alembic -c /api/alembic-backup.ini downgrade $(VERSION)

auto-revision-backup-db:
ifndef MESSAGE
	$(error 'MESSAGE is not set. Usage: make auto-revision-backup-db MESSAGE="message"')
endif
	@$(COMPOSE_DEV) exec api alembic -c /api/alembic-backup.ini revision --autogenerate -m "$(MESSAGE)"
	@$(COMPOSE_DEV) exec api chmod -R o+w src/migrations


################################################################################
# Testing
################################################################################


TEST_PATH =
tests:
	@$(COMPOSE_DEV) exec db psql -U postgres -c "DROP DATABASE IF EXISTS test_dbdt;"
	@$(COMPOSE_DEV) exec db psql -U postgres -c "DROP DATABASE IF EXISTS test_dbdt_backup;"

	@$(COMPOSE_DEV) exec api sh -c "pytest -vv -q -s $(TEST_PATH)"

checks:
	@$(MAKE) check-db
	@$(MAKE) flint
	@$(MAKE) ftests
	@$(MAKE) lint
	@$(MAKE) tests
	@$(MAKE) fbuild


################################################################################
# Frontend
################################################################################


flint:
	@cd frontend && npm run lint

ftests:
	@cd frontend && npm test

fbuild:
	@cd frontend && npm run build


################################################################################
# Pre Production
################################################################################


start-pre-prod:
	@$(COMPOSE_PRE_PROD) --env-file .env.prod up -d

stop-pre-prod:
	@$(COMPOSE_PRE_PROD) --env-file .env.prod stop

restart-pre-prod:
	$(MAKE) stop-pre-prod
	$(MAKE) start-pre-prod
	$(MAKE) check-db-pre-prod

remove-pre-prod:
	@$(COMPOSE_PRE_PROD) --env-file .env.prod down

check-db-pre-prod:
	@$(COMPOSE_PRE_PROD) exec api alembic -c /api/alembic.ini check
	@$(COMPOSE_PRE_PROD) exec api alembic -c /api/alembic-backup.ini check

upgrade-db-pre-prod:
	@$(COMPOSE_PRE_PROD) exec api sh -c "alembic -c /api/alembic.ini upgrade head"
	@$(COMPOSE_PRE_PROD) exec api sh -c "alembic -c /api/alembic-backup.ini upgrade head"


################################################################################
# Production
################################################################################


start-prod:
	@$(COMPOSE_PROD) --env-file .env.prod up -d

stop-prod:
	@$(COMPOSE_PROD) --env-file .env.prod stop

restart-prod:
	$(MAKE) stop-prod
	$(MAKE) start-prod
	$(MAKE) check-db-prod

remove-prod:
	@$(COMPOSE_PROD) --env-file .env.prod down

check-db-prod:
	@$(COMPOSE_PROD) exec api alembic -c /api/alembic.ini check
	@$(COMPOSE_PROD) exec api alembic -c /api/alembic-backup.ini check

upgrade-db-prod:
	@$(COMPOSE_PROD) exec api sh -c "alembic -c /api/alembic.ini upgrade head"
	@$(COMPOSE_PROD) exec api sh -c "alembic -c /api/alembic-backup.ini upgrade head"
