---
myst:
  html_meta:
    "description": "Comprehensive guide to configuring and running content migrations with collective.transmute, including project setup, pipeline configuration, reporting, and troubleshooting."
    "property=og:description": "How to set up, configure, and run content migrations using collective.transmute. Includes pipeline steps, TOML configuration, CLI usage, and migration reporting."
    "property=og:title": "Migration Usage Guide | collective.transmute"
    "keywords": "Plone, collective.transmute, CLI, Python, migration, pipeline, TOML, report, glossary, content types, blocks, Volto, exportimport, transmogrifier"

---

# Usage

This guide provides step-by-step instructions for running {term}`collective.transmute` with your own configuration.

## Creating a new project

First, you probably want to create a new Python project to host your {term}`transmute` configuration files, pipeline steps and type converters.

Our suggestion is to use {term}`uv` to create a new codebase (in our case, to be named **`plone-migration`**) by running the following command:

```shell
uv init --app --package plone-migration
```

Then edit the generated {file}`pyproject.toml`, add {term}`collective.transmute` as a dependency:

```toml
dependencies = [
    "collective.transmute"
]
```

And generate an initial {file}`transmute.toml` file at the top-level of your package by running:

```shell
uv run transmute settings generate
```

## Configuring your migration: The {file}`transmute.toml` file

The {file}`transmute.toml` file is a configuration file written in [TOML](https://toml.io/en/) format. It organizes all the settings needed to control how the migration pipeline runs. Each section is marked by a header in square brackets (for example, `[pipeline]`, `[types]`), and settings are grouped by their purpose—such as pipeline steps, type mappings, review state filters, and more.

- **Sections**: Each section defines a logical part of the migration process, like pipeline steps, principals, default pages, review state, paths, images, sanitization, and type conversions.
- **Arrays and Tables**: Lists of values (arrays) are written in square brackets, while more complex mappings (tables) use nested headers or double brackets for repeated entries.
- **Extensibility**: You can add or modify sections to customize your migration, such as adding new pipeline steps or defining how specific {term}`Plone` types are handled.
- **Comments**: Lines starting with `#` are comments and are ignored by the parser.

This file should be placed at the root of your migration project and edited to match your migration needs. For more details on TOML syntax, see [the TOML documentation](https://toml.io/en/).


## `transmute` command line

If you have installed {term}`collective.transmute` in your project or local Python virtual environment, you should have the `transmute` command line application available.

```shell
uv run transmute
```

Take a look at all the available options in the [CLI](cli.md) documentation.

## Preparing the migration

We always recommend you to run `uv run transmute report /exported-data/ report-raw-data.json` to generate a report of the data you are going to migrate.

The report will contain:
* A breakdown of number of content items by content types, creators and review states;
* Number of contents using a given layout view, per content type;
* Number of contents with a given tag (subjects);

These information is important when planning a new migration, as you can adapt the settings present on {file}`transmute.toml` to adjust the migration to your needs.

## Running a migration

After reviewing the {file}`transmute.toml` settings, and making sure the exported data (exported using {term}`collective.exportimport`) is reachable, run the transmute process with the command:

```shell
uv run transmute run --clean-up --write-report /exported-data/ /transmuted-data/
```

This command will, first remove the results of previous migrations (`--clean-up`) and will generate a `report_transmute.csv` file with the result of the transmute.

### Understanding `report_transmute.csv`

This file contains the report, as CSV, of the last transmute process. The file has the following columns:

* `filename`: Original file name of the processed item
* `src_path`: Item Path in the source {term}`Plone` portal
* `src_uid`: Original UID for the item
* `src_type`: Original portal type for the item
* `src_state`: Original review state
* `dst_path`: Item path in the destination portal
* `dst_uid`: Item UID in the destination portal
* `dst_type`: Item portal type at destination
* `dst_state`: Item review state
* `last_step`: If present, shows the step of the pipeline where the item was dropped

Example of an item that was dropped (in this case, replaced) because there was another item as default page applied to it:

```csv
53642.json,/joaopessoa/editais,0a509104d4124a548e2a18b15c100cf2,Folder,published,--,--,--,--,process_default_page
```

```{note}
When an item is dropped, all columns starting with `dst_` will display the value `--`
```

Example of an item that was moved and had its original portal type changed:
```csv
53643.json,/joaopessoa/editais/assistencia-estudantil,d11db7bccae94ec48f0e1a9b669bf67a,Folder,published,/campus/joaopessoa/editais/assistencia-estudantil,d11db7bccae94ec48f0e1a9b669bf67a,Document,published,
```

## Common issues

### Running `transmute run` seems to be stuck

This could happen because of an unhandled exception, so we suggest you run the same command again, but passing the `--no-ui` option to see the full traceback.

```shell
uv run transmute run --no-ui --clean-up --write-report /exported-data/ /transmuted-data/
```

### Adding a `breakpoint` to my own step or type processor

If you want to debug your code and add a breakpoint to it, you need to use the `--no-ui` option.
