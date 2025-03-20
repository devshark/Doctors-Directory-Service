# customize as needed
VENV_DIR := .venv

.PHONY: init run test clean build run-docker help new-migration migrations migrate loaddata makemessages compilemessages

default: init

# install virtualenv and dependencies
# let the user activate the virtual environment manually. 
# It's not easy to do in a Makefile, because it opens a new shell on every line.
init:
	@python3 -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install -r requirements.txt
	@echo "run 'source $(VENV_DIR)/bin/activate' to activate the virtual environment"

run: 
	@$(VENV_DIR)/bin/python manage.py runserver 0.0.0.0:8000

test:
	@$(VENV_DIR)/bin/python manage.py test

new-migration:
	@$(VENV_DIR)/bin/python manage.py makemigrations doctors_api --empty --name $(name)

migrations:
	@$(VENV_DIR)/bin/python manage.py makemigrations
	@$(VENV_DIR)/bin/python manage.py makemigrations doctors_api

migrate:
	@$(VENV_DIR)/bin/python manage.py migrate

loaddata:
	@$(VENV_DIR)/bin/python manage.py loaddata doctors_api/fixtures/categories.json
	@$(VENV_DIR)/bin/python manage.py loaddata doctors_api/fixtures/districts.json
	@$(VENV_DIR)/bin/python manage.py loaddata doctors_api/fixtures/doctors.json

makemessages:
	@$(VENV_DIR)/bin/python manage.py makemessages -l en
	@$(VENV_DIR)/bin/python manage.py makemessages -l zh_Hans
	@$(VENV_DIR)/bin/python manage.py makemessages -l zh_Hant

compilemessages:
	@$(VENV_DIR)/bin/python manage.py compilemessages -l en
	@$(VENV_DIR)/bin/python manage.py compilemessages -l zh_Hans
	@$(VENV_DIR)/bin/python manage.py compilemessages -l zh_Hant

# clean up the virtual environment and cache
clean:
	rm -rf $(VENV_DIR)
	find . -type f -name *.pyc -delete
	find . -type d -name __pycache__ -delete

build:
	docker build -t doctors-api:latest .

run-docker: build
	docker compose up

help:
	@echo "make build - build the docker image"
	@echo "make clean - clean up the virtual environment and cache"
	@echo "make compilemessages - compile locale files (.mo)"
	@echo "make help - show this help message"
	@echo "make init - initialize the virtual environment"
	@echo "make loaddata - load data from fixtures"
	@echo "make makemessages - create locale files (.po)"
	@echo "make migrate - apply the migration scripts to the database"
	@echo "make migrations - create migration scripts"
	@echo "make new-migration - create a new migration script"
	@echo "make run - run the application"
	@echo "make run-docker - run the docker container"
	@echo "make test - run the tests"
