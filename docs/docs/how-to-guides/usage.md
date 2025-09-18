---
myst:
  html_meta:
    "description": "Comprehensive guide to configuring and running content migrations with collective.transmute, including project setup, pipeline configuration, reporting, and troubleshooting."
    "property=og:description": "How to set up, configure, and run content migrations using collective.transmute. Includes pipeline steps, TOML configuration, CLI usage, and migration reporting."
    "property=og:title": "Migration Usage Guide | collective.transmute"
    "keywords": "Plone, collective.transmute, CLI, Python, migration, pipeline, TOML, report, content types, blocks, Volto, exportimport, transmogrifier"

---

# Usage

This guide provides step-by-step instructions for using {term}`collective.transmute` with your own project, and managing its configuration files, pipeline steps, and type converters.
It uses {term}`uv`.

```{seealso}
[Installing uv](https://docs.astral.sh/uv/getting-started/installation/)
```


## Create a new project

Use uv to create a new project named `plone-migration` by running the following command.

```shell
uv init --app --package plone-migration
```

Then edit the generated {file}`pyproject.toml`, adding `collective.transmute` as a dependency.

```toml
dependencies = [
    "collective.transmute"
]
```

Next, generate an initial {file}`transmute.toml` file at the top-level of your project by running the following command.

```shell
uv run transmute settings generate
```


## Configure your migration in {file}`transmute.toml`

The {file}`transmute.toml` file is a configuration file written in {term}`TOML` format.
It organizes all the settings needed to control how the migration pipeline runs.
Each section is marked by a header in square brackets, such as `[pipeline]` or `[types]`.
Settings are grouped by their purpose, such as pipeline steps, type mappings, review state filters, and more.

Sections
:   Each section defines a logical part of the migration process, such as pipeline steps, principals, default pages, review state, paths, images, sanitization, and type conversions.

Arrays and Tables
:   Lists of values (arrays) are written in square brackets, while more complex mappings (tables) use nested headers or double brackets for repeated entries.

Extensibility
:   You can add or modify sections to customize your migration, such as adding new pipeline steps or defining how specific {term}`Plone` types are handled.

Comments
:   Lines starting with `#` are comments and are ignored by the parser.

This file should be placed at the root of your migration project and edited to match your migration needs.

```{seealso}
For more details on TOML syntax, see [the TOML documentation](https://toml.io/en/).
```


## `transmute` command line

If you have installed `collective.transmute` in your project or local Python virtual environment, you should have the `transmute` command line application available.

```shell
uv run transmute
```

Take a look at all the available options in the {doc}`cli` documentation.


## Prepare the migration

It's strongly recommended to always generate a report of the data you're going to migrate before you do an actual migration.
Use the following command to generate a report.

```shell
uv run transmute report /exported-data/ report-raw-data.json
```

The report will contain the following information.

-   a breakdown of the number of content items, listed by content types, creators, and review states
-   the number of content items using a given layout view, per content type
-   the number of content items with a given tag (subjects)

This information is important when planning a new migration, as you can adapt the settings present in {file}`transmute.toml` to adjust the migration to your needs.


## Run a migration

After reviewing the {file}`transmute.toml` settings, and making sure the exported data (exported using {term}`collective.exportimport`) is reachable, run the transmute process with the following command.

```shell
uv run transmute run --clean-up --write-report /exported-data/ /transmuted-data/
```

This command will first remove the results of previous migrations (`--clean-up`), then will generate a {file}`report_transmute.csv` file with the result of the transmute.


### Understanding {file}`report_transmute.csv`

This file contains the report, as CSV, of the last transmute process.
The file has the following columns.

`filename`
:   Original file name of the processed item.

`src_path`
:   Item Path in the source {term}`Plone` portal.

`src_uid`
:   Original UID for the item.

`src_type`
:   Original portal type for the item.

`src_state`
:   Original review state.

`dst_path`
:   Item path in the destination portal.

`dst_uid`
:   Item UID in the destination portal.

`dst_type`
:   Item portal type at destination.

`dst_state`
:   Item review state.

`last_step`
:   If present, shows the step of the pipeline where the item was dropped.

`status`
:   If the item was processed or dropped.

`src_level`
:   Navigation level, from Portal root, of the source item. It will return `—1` if source item did not exist.

`dst_level`
:   Navigation level, from Portal root, of the item. It will return `—1` if item was dropped.

The following is an example of an item that was dropped (in this case, replaced) because there was another item as the default page which was applied to it.

```csv
53642.json,/joaopessoa/editais,0a509104d4124a548e2a18b15c100cf2,Folder,published,--,--,--,--,process_default_page
```

```{note}
When an item is dropped, all columns starting with `dst_` will display the value `--`
```

The following is an example of an item that was moved and had its original portal type changed.

```csv
53643.json,/joaopessoa/editais/assistencia-estudantil,d11db7bccae94ec48f0e1a9b669bf67a,Folder,published,/campus/joaopessoa/editais/assistencia-estudantil,d11db7bccae94ec48f0e1a9b669bf67a,Document,published,
```

## Common issues

The following are some common issues you might encounter when running a migration.

### `transmute` command not found

Make sure you've installed `collective.transmute` in your project or local Python virtual environment.

### `transmute run` seems to be stuck

This could happen because of an unhandled exception.
Try to run the same command again, but passing the `--no-ui` option to see the full traceback.

```shell
uv run transmute run --no-ui --clean-up --write-report /exported-data/ /transmuted-data/
```

### Debug a migration

If you want to debug your code and add a breakpoint to it, use the `--no-ui` option.
