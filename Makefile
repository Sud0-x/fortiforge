APP=fortiforge
PY=python3
PIP=pip
VENV?=.venv

.PHONY: help install dev test lint format build docker-build docker-run sandbox-up sandbox-down demo

help:
	@echo "Targets: install dev test lint format build docker-build docker-run sandbox-up sandbox-down demo"

install:
	$(PY) -m venv $(VENV)
	. $(VENV)/bin/activate && $(PIP) install -U pip && $(PIP) install -e . -r requirements.txt

dev:
	. $(VENV)/bin/activate && $(PIP) install -e . -r requirements.txt

test:
	. $(VENV)/bin/activate && pytest -q

lint:
	@echo "(Basic) Linting not configured; consider adding ruff/flake8."

format:
	@echo "(Basic) Formatting not configured; consider adding black/ruff." 

build:
	. $(VENV)/bin/activate && scripts/build_bundle.sh

docker-build:
	docker build -t fortiforge:latest .

docker-run:
	docker run --rm -it -v $$HOME/.fortiforge:/root/.fortiforge fortiforge:latest fortiforge --help

sandbox-up:
	docker compose -f sandbox/docker-compose.yml up -d --build

sandbox-down:
	docker compose -f sandbox/docker-compose.yml down -v

demo:
	bash scripts/demo_commands.sh