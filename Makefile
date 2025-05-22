PYTHON = $(shell which python3.12)
SHELL = /bin/bash
VENV_DIR = .venv

install: $(VENV_DIR)

$(VENV_DIR): requirements.txt
	@$(PYTHON) -m venv $@
	@$(VENV_DIR)/bin/python -m pip install --quiet --upgrade pip
	@$(VENV_DIR)/bin/python -m pip install --quiet --requirement=$<
	touch $@

.PHONY: lint
lint: $(VENV_DIR)
	@$</bin/python -m pip install --quiet pre-commit pytest
	@$</bin/pre-commit install
	@$</bin/pre-commit run --all-files

.PHONY: test
test: lint
	@$(VENV_DIR)/bin/pytest test_tabs.py

.PHONY: clean
clean:
	@git clean -fdfx
