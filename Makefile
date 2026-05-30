################################################################################
# Development
################################################################################


start:
	@docker compose -f docker-compose.dev.yaml up -d

fstart:
	@docker compose -f docker-compose.dev.yaml watch

stop:
	@docker compose -f docker-compose.dev.yaml stop

build:
	@docker compose -f docker-compose.dev.yaml build

build-no-cache:
	@docker compose -f docker-compose.dev.yaml build --no-cache

remove:
	@docker compose -f docker-compose.dev.yaml down --remove-orphans

destroy:
	@docker compose -f docker-compose.dev.yaml down -v --remove-orphans

logs:
	@docker compose -f docker-compose.dev.yaml logs -f

restart:
	$(MAKE) stop
	$(MAKE) start

rebuild:
	$(MAKE) stop
	$(MAKE) build
	$(MAKE) start

reset:
	$(MAKE) stop
	$(MAKE) build-no-cache
	$(MAKE) start


lint:
	@uv run ruff check ./src
	@uv run ty check ./src


################################################################################
# Database
################################################################################


upgrade-db:
	@docker compose -f docker-compose.dev.yaml exec api alembic -c /api/alembic.ini upgrade head

VERSION ?= -1
downgrade-db:
	@echo "Downgrading to/by $(VERSION) version"
	@docker compose -f docker-compose.dev.yaml exec api alembic -c /api/alembic.ini downgrade $(VERSION)

auto-revision-db:
ifndef MESSAGE
	$(error 'MESSAGE is not set. Usage: make auto-revision-db MESSAGE="message"')
endif
	@docker compose -f docker-compose.dev.yaml exec api alembic -c /api/alembic.ini revision --autogenerate -m "$(MESSAGE)"


################################################################################
# Testing
################################################################################


.PHONY: tests
TEST_PATH =
tests:
#	In case the tests fail and database wasnt deleted
	@docker compose -f docker-compose.dev.yaml exec db psql -U postgres -c "DROP DATABASE IF EXISTS test_dbdt;"

# Test execution
	@docker compose -f docker-compose.dev.yaml exec db psql -U postgres -c "CREATE DATABASE test_dbdt;"
	@docker compose -f docker-compose.dev.yaml exec api sh -c "pytest -vv -q -s $(TEST_PATH)"
	@docker compose -f docker-compose.dev.yaml exec db psql -U postgres -c "DROP DATABASE test_dbdt;"


test-db:
	docker run -d --name postgres-testing -e POSTGRES_PASSWORD=testing -e POSTGRES_USER=testing -e POSTGRES_DB=testing -p 5435:5432 postgres:latest


checks:
	@$(MAKE) lint
	@$(MAKE) flint
	@$(MAKE) tests


################################################################################
# Frontend
################################################################################


npm-install:
	@cd frontend && npm i $@


flint:
	@cd frontend && npm run lint


################################################################################
# Production
################################################################################


start-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d

stop-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod stop

restart-prod:
	$(MAKE) stop-prod
	$(MAKE) start-prod

remove-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod down
