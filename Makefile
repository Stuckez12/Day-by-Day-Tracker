################################################################################
# Development
################################################################################


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


linters:
	@uv run black --check backend
	@uv run mypy backend
	@uv run flake8 backend --select=E225,E231,E302,E305,F403,F404,F405,F821,F822,F823,F824 --exclude "*/__init__.py"
	@uv run flake8 backend --select=F403,F405 --filename="*/__init__.py" --exclude ".venv"


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
	pytest -vv $(TEST_PATH)


test-db:
	docker run -d --name postgres-testing -e POSTGRES_PASSWORD=testing -e POSTGRES_USER=testing -e POSTGRES_DB=testing -p 5435:5432 postgres:latest


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

restart-prod:
	$(MAKE) stop-prod
	$(MAKE) start-prod

remove-prod:
	@docker compose -f docker-compose.prod.yaml --env-file .env.prod down
