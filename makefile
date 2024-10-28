.PHONY: help

help: # List commands and their descriptions
	@grep -E '^[a-zA-Z0-9_-]+: # .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ": # "; printf "\n\033[93;01m%-30s %-30s\033[0m\n\n", "Command", "Description"}; {split($$1,a,":"); printf "\033[96m%-30s\033[0m \033[92m%s\033[0m\n", a[1], $$2}'

build: # Build the docker images
	docker compose build

up: # Bring up the docker containers
	docker compose up

down: # Bring down the docker containers
	docker compose down

# Run a command in a new container
run = docker compose run --rm

# Run a command in a new container without starting linked services
run-no-deps = $(run) --no-deps

# Run a command in an existing container
exec = docker compose exec

#
# Makefile variables
#

chown = $(web) chown $(shell id -u):$(shell id -g)

manage = python manage.py

# Run on existing container if available otherwise a new one
web := ${if $(shell docker ps -q -f name=web),$(exec) web,$(run) web}
db := ${if $(shell docker ps -q -f name=postgres),$(exec) postgres,$(run) postgres}

setup: # Set up the project from scratch
	make build
	npm install
	npm run build
	poetry install
	make migrate
	make up

vite: # Run vite
	npm run dev

bash: # Open up a bash in the web container
	$(web) /bin/bash

shell: # Open up a python shell in the web container
	$(web) $(manage) shell_plus

migrations: # Run makemigrations
	$(web) $(manage) makemigrations
	$(chown) */migrations/*

empty-migration: # Create an empty migration
	$(web) $(manage) makemigrations --empty $(app) --name $(name)
	$(chown) */migrations/*

check-migrations: # Check if there are any missing migrations
	$(web) $(manage) makemigrations --check

merge-migrations: # Merge migrations to resolve conflicts
	$(web) $(manage) makemigrations --merge

migrate: # Run migrations against the local db
	$(web) $(manage) migrate

manage-groups: # Set permissions across the app
	$(web) $(manage) manage_groups

superuser: # Creates a superuser
	$(web) $(manage) createsuperuser

dumpdata: # Run django `dumpdata` command and output to a file
	$(web) $(manage) dumpdata $(model) --indent 4 -o $(output)
	$(chown) $(output)

check-django: # Run deployment checklist
	$(web) $(manage) check --deploy

# Formatters
black: # Run black
	poetry run black .

isort: # Run isort
	poetry run isort .

fix: # Run project formatting
	make black
	make isort

# Checks
check-black: # Run black with `--check` flag
	poetry run black --check .

check-isort: # Run isort with `--check` flag
	poetry run isort --check .

check-mypy: # Run mypy
	poetry run mypy .

check: # Run project checks
	make check-black
	make check-isort
	make check-mypy
	make check-migrations

# Tests
test: # Run pytest, use the optional arg `tests` to run specific tests, eg: `make test tests=path/to/test.py::ClassName::test_func_name`
	$(web) pytest $(tests)

test-fresh: # The same as `make test` but with a fresh db
	$(web) pytest --create-db $(tests)

coverage: # Run test with pytest and generate coverage report
	$(web) coverage run -m pytest --create-db $(tests)
	$(web) coverage report --fail-under=75

coverage-html: # Generate a html report of the test coverage
	$(web) coverage html
	poetry run python -m webbrowser htmlcov/index.html

# DB
db-reset: # Reset the database
	docker compose stop postgres
	docker compose rm -f postgres
	docker compose up -d postgres

db-shell: # Open the database container postgres shell
	$(db) psql --username postgres

DUMP_NAME = local

db-dump: # Dump the current database, use `DUMP_NAME` to change the name of the dump
	@PGPASSWORD='postgres' pg_dump postgres -U postgres -h localhost -p 5432 -O -x -c -f ./.dumps/$(DUMP_NAME).dump

db-from-dump: # Load a dumpped database, use `DUMP_NAME` to change the name of the dump
	@PGPASSWORD='postgres' psql -h localhost -U postgres postgres -f ./.dumps/$(DUMP_NAME).dump

# Make Docs
serve-docs: # Serve mkdocs on port 8002
	poetry run mkdocs serve -a localhost:8002