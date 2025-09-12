# Makefile for Sphinx documentation
.DEFAULT_GOAL   = help
SHELL           = bash

# You can set these variables from the command line.
SPHINXOPTS      ?=
PAPER           ?=

# Internal variables.
GREEN=`tput setaf 2`
RESET=`tput sgr0`
SPHINXBUILD     = "$(realpath .venv/bin/sphinx-build)"
DOCS_DIR        = ./docs/
BUILDDIR        = ./_build
PAPEROPT_a4     = -D latex_paper_size=a4
PAPEROPT_letter = -D latex_paper_size=letter
ALLSPHINXOPTS   = -d $(BUILDDIR)/doctrees $(PAPEROPT_$(PAPER)) $(SPHINXOPTS) $(DOCS_DIR)
VALEFILES       := $(shell find $(DOCS_DIR) -type f -name "*.md" -print)
VALEOPTS        ?=
PYTHONVERSION   = >=3.11,<3.14

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help:  # This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


# environment management
.venv/bin/python:  ## Create Python virtual environment and install package requirements
	@uv sync

.PHONY: install
install:  .venv/bin/python ## Sync package requirements


.PHONY: init
init: clean clean-python .venv/bin/python  ## Clean docs build directory and Python, and initialize Python virtual environment

.PHONY: clean
clean:  ## Clean docs build directory
	cd $(DOCS_DIR) && rm -rf $(BUILDDIR)/

.PHONY: clean-python
clean-python: clean
	rm -rf .venv/
	rm -rf *.egg-info
# /environment management


# documentation builders

.PHONY: changelog
changelog: .venv/bin/python  ## Copy the changelog to the docs
	cp ../CHANGELOG.md ./docs/CHANGELOG.md
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."


.PHONY: html
html: changelog  ## Build html
	@uv run sphinx-build -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

.PHONY: livehtml
livehtml: changelog  ## Rebuild Sphinx documentation on changes, with live-reload in the browser
	@uv run sphinx-autobuild \
		--ignore "*.swp" \
		--port 8050 \
		-b html $(DOCS_DIR) "$(BUILDDIR)/html" $(SPHINXOPTS) $(O)

.PHONY: dirhtml
dirhtml: changelog
	@uv run sphinx-build -b dirhtml $(ALLSPHINXOPTS) $(BUILDDIR)/dirhtml
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/dirhtml."

.PHONY: singlehtml
singlehtml: changelog
	@uv run sphinx-build -b singlehtml $(ALLSPHINXOPTS) $(BUILDDIR)/singlehtml
	@echo
	@echo "Build finished. The HTML page is in $(BUILDDIR)/singlehtml."

.PHONY: text
text: .changelog
	@uv run sphinx-build -b text $(ALLSPHINXOPTS) $(BUILDDIR)/text
	@echo
	@echo "Build finished. The text files are in $(BUILDDIR)/text."

.PHONY: changes
changes: changelog
	@uv run sphinx-build -b changes $(ALLSPHINXOPTS) $(BUILDDIR)/changes
	@echo
	@echo "The overview file is in $(BUILDDIR)/changes."

.PHONY: rtd-prepare
rtd-prepare:  ## Prepare environment on Read the Docs
	asdf plugin add uv
	asdf install uv latest
	asdf global uv latest

.PHONY: rtd-pr-preview  ## Build pull request previews on Read the Docs
rtd-pr-preview: rtd-prepare .venv/bin/python ## Build pull request preview on Read the Docs
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) ${READTHEDOCS_OUTPUT}/html/

.PHONY: build
build: html  ## Build documentation in HTML format

# /documentation builders


# test
.PHONY: linkcheck
linkcheck: changelog  ## Run linkcheck
	@uv run sphinx-build -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: linkcheckbroken
linkcheckbroken: changelog  ## Run linkcheck and show only broken links
	@uv run sphinx-build -b linkcheck $(ALLSPHINXOPTS) $(BUILDDIR)/linkcheck | GREP_COLORS='0;31' grep -wi "broken\|redirect" --color=always | GREP_COLORS='0;31' grep -vi "https://github.com/plone/volto/issues/" --color=always && if test $$? = 0; then exit 1; fi || test $$? = 1
	@echo
	@echo "Link check complete; look for any errors in the above output " \
		"or in $(BUILDDIR)/linkcheck/ ."

.PHONY: doctest
doctest: changelog  ## Test snippets in the documentation
	@uv run sphinx-build -b doctest $(ALLSPHINXOPTS) $(BUILDDIR)/doctest
	@echo "Testing of doctests in the sources finished, look at the " \
	      "results in $(BUILDDIR)/doctest/output.txt."

.PHONY: vale
vale: changelog  ## Run Vale style, grammar, and spell checks
	@uv run vale sync
	@uv run vale --no-wrap $(VALEOPTS) $(VALEFILES)
	@echo "Vale is finished; look for any errors in the above output."
	@echo

.PHONY: test
test: clean vale linkcheckbroken doctest  ## Clean docs build, then run vale, linkcheckbroken, and doctest

.PHONY: all
all: clean vale linkcheckbroken html  ## Clean docs build, then run linkcheckbroken, and build html
# /test
