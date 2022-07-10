PYTHON_BINS ?= ./.venv/bin
PYTHON ?= ${PYTHON_BINS}/python
PYTHONPATH ?= ${PWD}/src

.PHONY: install
install: .venv/bin/poetry
	${PYTHON_BINS}/mpoetry install

.PHONY: dev
dev: .venv
	${PYTHON_BINS}/mkdocs serve 

.PHONY: build
build: .venv
	${PYTHON_BINS}/mkdocs build 

.venv:
	python shell use 3.10.4 && \
		python -m venv .venv

.venv/bin/poetry: .venv
	${PYTHON_BINS}/pip install -U pip poetry
