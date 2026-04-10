### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Python checks
UV?=uv

# installed?
ifeq (, $(shell which $(UV) ))
  $(error "UV=$(UV) not found in $(PATH)")
endif

BACKEND_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

GIT_FOLDER=$(BACKEND_FOLDER)/.git
VENV_FOLDER=$(BACKEND_FOLDER)/.venv
BIN_FOLDER=$(VENV_FOLDER)/bin


all: build

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


############################################
# Installation
############################################

$(BIN_FOLDER)/pytest: ## Install dependencies
	@echo "$(GREEN)==> Install environment$(RESET)"
	@uv sync

 $(BIN_FOLDER)/ruff: $(BIN_FOLDER)/pytest

.PHONY: install
install: $(BIN_FOLDER)/pytest ## Install package

.PHONY: clean
clean: ## Clean environment
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	rm -rf $(VENV_FOLDER) .python-version .venv .ruff_cache .pytest_cache uv.lock

############################################
# Linting
############################################
.PHONY: lint-mypy
lint-mypy: $(BIN_FOLDER)/mypy ## Check type hints
	@echo "$(GREEN)==> Check type hints$(RESET)"
	@uv run mypy src

.PHONY: lint
lint: $(BIN_FOLDER)/ruff ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Lint codebase$(RESET)"
	@uvx ruff@latest check --fix
	@uvx pyroma@latest -d .
	@uvx check-python-versions@latest .
	$(MAKE) lint-mypy

############################################
# Formatting
############################################
.PHONY: format
format: $(BIN_FOLDER)/ruff ## Check and fix code base according to Plone standards
	@echo "$(GREEN)==> Format codebase$(RESET)"
	@uvx ruff@latest check --select I --fix
	@uvx ruff@latest format

############################################
# Tests
############################################
.PHONY: test
test: $(BIN_FOLDER)/pytest ## run tests
	@uv run pytest

.PHONY: test-coverage
test-coverage: ## Test the code with pytest
	@echo "🚀 Testing code: Running pytest"
	@uv run coverage run -m pytest
	@uv run coverage combine
	@uv run coverage report

############################################
# Documentation
############################################
.PHONY: docs-html
docs-html: $(VENV_FOLDER) ## Build HTML documentation
	@make -C ./docs html

.PHONY: docs-livehtml
docs-livehtml: $(VENV_FOLDER) ## Build documentation and serve it
	@make -C ./docs livehtml

.PHONY: docs-vale
docs-vale: $(VENV_FOLDER) ## Run vale on the documentation
	@make -C ./docs vale

.PHONY: docs-linkcheckbroken
docs-linkcheckbroken: $(VENV_FOLDER) ## Run checks for broken links
	@make -C ./docs linkcheckbroken

.PHONY: docs-test
docs-test: $(VENV_FOLDER) ## Run tests on the documentation
	@make -C ./docs test

############################################
# Release
############################################
.PHONY: changelog
changelog: ## Release the package to pypi.org
	@echo "🚀 Display the draft for the changelog"
	@uv run towncrier --draft

.PHONY: release
release: ## Release the package to pypi.org
	@echo "🚀 Release package"
	@uv run prerelease
	@uv run release
	@rm -Rf dist
	@uv build
	@uv publish
	@uv run postrelease
