---
myst:
  html_meta:
    "description": "Terms and definitions used throughout the documentation."
    "property=og:description": "Terms and definitions used throughout the documentation."
    "property=og:title": "Glossary"
    "keywords": "Plone, documentation, glossary, term, definition"
---

This glossary provides example terms and definitions relevant to `collective.transmute`.

(glossary-label)=

# Glossary

```{glossary}
:sorted: true

Plone
    [Plone](https://plone.org/) is an open-source content management system that is used to create, edit, and manage digital content, like websites, intranets and custom solutions.
    It comes with over twenty years of growth, optimizations, and refinements.
    The result is a system trusted by governments, universities, businesses, and other organizations all over the world.

add-on
    An add-on in Plone extends its functionality.
    It is code that is released as a package to make it easier to install.

    In Volto, an add-on is a JavaScript package.

    In Plone core, an add-on is a Python package.

    -   [Plone core add-ons](https://github.com/collective/awesome-plone#readme)
    -   [Volto add-ons](https://github.com/collective/awesome-volto#readme)
    -   [Add-ons tagged with the trove classifier `Framework :: Plone` on PyPI](https://pypi.org/search/?c=Framework+%3A%3A+Plone)

blocks
    Blocks are the fundamental components of a page layout in {term}`Volto`.

Slate
    [Slate.js](https://docs.slatejs.org/) is a highly customizable platform for creating rich-text editors, also known as {term}`WYSIWYG` editors.
    It enables you to create powerful, intuitive editors similar to those you've probably used in Medium, Dropbox Paper, or Google Docs.

`volto-slate`
    `volto-slate` is an interactive default text editor for Volto, developed on top of {term}`Slate`, offering enhanced {term}`WYSIWYG` functionality and behavior.

Volto
    [Volto](https://github.com/plone/volto) is a React-based frontend for Plone.

CMS
    Content Management System

REST
    REST stands for [Representational State Transfer](https://en.wikipedia.org/wiki/Representational_state_transfer).
    It is a software architectural principle to create loosely coupled web APIs.

collective.transmogrifier
Transmogrifier
    [Transmogrifier](https://github.com/collective/collective.transmogrifier), or `collective.transmogrifier`, provides support for building pipelines that turn one thing into another.
    Specifically, transmogrifier pipelines are used to convert and import legacy content into a Plone site.
    It provides the tools to construct pipelines from multiple sections, where each section processes the data flowing through the pipe.

collective.exportimport
    [`collective.exportimport`](https://github.com/collective/collective.exportimport) is a package to export and import content, members, relations, translations, localroles and much more.

plone.exportimport
    [`plone.exportimport`](https://github.com/plone/plone.exportimport) is a {term}`Plone` core package that enables extraction and loading of content in a JSON format.

collective.transmute
    [`collective.transmute`](https://github.com/collective/collective.transmute) is a package to convert data from {term}`collective.exportimport` to {term}`plone.exportimport`.

pytest
    [pytest](https://docs.pytest.org/) is a Python test framework that makes it easy to write small, readable tests, and can scale to support complex functional testing for applications and libraries.

setuptools
    [setuptools](https://setuptools.pypa.io/) is a Python package development and distribution library.
    It is commonly used to build, package, and install Python projects, especially those using a {file}`setup.py` file.

PEP 621
    [PEP 621](https://peps.python.org/pep-0621/) is a Python Enhancement Proposal that standardizes how project metadata is specified in {file}`pyproject.toml` files for Python packages.

uv
    [uv](https://github.com/astral-sh/uv) is a fast Python package manager and build tool that supports modern workflows, including dependency management via {file}`pyproject.toml`.

pyproject.toml
    {file}`pyproject.toml` is a configuration file for Python projects that defines build system requirements, dependencies, and project metadata.
    It is used by modern Python packaging tools and specified by PEP 518 and PEP 621.

Typer
    [Typer](https://typer.tiangolo.com/) is a Python library for building command-line interfaces (CLIs) using type hints, automatic help generation, and minimal code.

CLI
    Command-Line Interface.
    A program that is operated by typing commands into a terminal or shell, rather than using a graphical user interface (GUI).

Converter
    In {term}`collective.transmute`, a converter is a component or function that transforms HTML content into Volto blocks or other structured formats.

Registration
    The process of making a converter, block, or other component available to the system, typically by adding it to a registry or configuration.

blocks_layout
    The structure that defines the order and arrangement of blocks within a Volto page or content item.
    It is usually represented as a JSON object.

Uvicorn
    [Uvicorn](https://www.uvicorn.org/) is a lightning-fast ASGI server implementation for Python, commonly used to run FastAPI applications.

OpenAPI
    [OpenAPI](https://www.openapis.org/) is a specification for describing RESTful APIs, enabling automatic documentation, client generation, and validation.

```
