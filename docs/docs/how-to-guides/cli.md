---
myst:
  html_meta:
    "description": "How to use the command line interface for collective.transmute, including commands, options, and server endpoints."
    "property=og:description": "Guide to using the command line interface and block converters in collective.transmute."
    "property=og:title": "How to use the CLI | collective.transmute"
    "keywords": "Plone, collective.transmute, command line interface, Typer, Volto, migration, guide"
---

# `transmute` command line application

Installing `collective.transmute` in your project will provide you with a new {term}`CLI` application named `transmute`.

You can either:

1.  locate the Python virtual environment used by your project (usually present in the `.venv` folder of your backend codebase) and run `.venv/bin/transmute`, or
1.  if your project uses `uv`, then run `uv run transmute`, and `uv` will correctly initiate the CLI application.

All examples here will showcase `uv run transmute` for the sake of simplicity.


## Application help

After running `uv run transmute`, you'll be presented with a list of options and commands available in the tool, powered by {term}`Typer`:

```console
 Usage: transmute [OPTIONS] COMMAND [ARGS]...

 Welcome to transmute, the utility to transform data from collective.exportimport to
 plone.exportimport.

╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --install-completion          Install completion for the current shell.               │
│ --show-completion             Show completion for the current shell, to copy it or    │
│                               customize the installation.                             │
│ --help                        Show this message and exit.                             │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ────────────────────────────────────────────────────────────────────────────╮
│ info       Show information about the collective.transmute tool and its main          │
│            dependencies.                                                              │
│ run        Transmutes data from src folder (in collective.exportimport format) to     │
│            plone.exportimport format in the dst folder.                               │
│ report     Generates a JSON file with a report of export data in src directory.       │
│ settings   Report settings to be used by this application.                            │
│ sanity     Run a sanity check on pipeline steps.                                      │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

## Commands

The `transmute` application provides five commands: `info`, `run`, `report`, `settings`, and `sanity`.


### `info`

This command displays information about the `collective.transmute` package and its main dependencies.

```shell
uv run transmute info
```

```console
collective.transmute - 1.0.0a0
==============================

Dependencies:
 - collective.html2blocks: 1.0.0a2
```

### `run`

This command runs the actual transmute process.

```shell
uv run transmute run --help
```

```console
 Usage: transmute run [OPTIONS] SRC DST

 Transmutes data from src folder (in collective.exportimport format) to
 plone.exportimport format in the dst folder.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────╮
│ *    src      PATH  Source path of the migration [required]                           │
│ *    dst      PATH  Destination path of the migration [required]                      │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --write-report    --no-write-report      Should we write a CSV report with all path   │
│                                          transformations?                             │
│                                          [default: no-write-report]                   │
│ --clean-up        --no-clean-up          Should we remove all existing files in the   │
│                                          dst?                                         │
│                                          [default: no-clean-up]                       │
│ --ui              --no-ui                Use rich UI [default: ui]                    │
│ --help                                   Show this message and exit.                  │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

Given a path to the source data `src` and a path to the transmuted data `dst` you can run this command as follows.

```shell
uv run transmute run /exported-data/ /transmuted-data/
```

#### Options

| Option | Description | Default Value |
| --- | --- | --- |
| `--clean-up` or `--no-clean-up` | Should we remove all existing files in the destination folder? |  `--no-clean-up` |
| `--ui` or `--no-ui` | Enable or disable the graphical interface | `--ui` |
| `--write-report` or `--write-report` | Should we write a CSV report with all path transformations?  | `--no-write-report` |
| `--help` | Show the help for the command | |


### `report`

This command generates a JSON file with a report of export data in `src` directory.

```shell
uv run transmute report --help
```

```console
 Usage: transmute report [OPTIONS] SRC [DST]

 Generates a JSON file with a report of export data in src directory.

╭─ Arguments ───────────────────────────────────────────────────────────────────────────╮
│ *    src      PATH   Source path of the migration data [required]                     │
│      dst      [DST]  Destination path of the report                                   │
╰───────────────────────────────────────────────────────────────────────────────────────╯
╭─ Options ─────────────────────────────────────────────────────────────────────────────╮
│ --report-types        TEXT  Portal types to report on. Please provide as              │
│                             comma-separated values.                                   │
│ --help                      Show this message and exit.                               │
╰───────────────────────────────────────────────────────────────────────────────────────╯
```

The following command will generate a report of all portal types in the `src` directory and save it to {file}`reports/report-raw-data.json`.

```shell
uv run transmute report /exported-data/ reports/
```


### `settings`

This command reports all settings used by `collective.transmute`

```shell
uv run transmute settings
```

```console
Settings used by this application
---------------------------------
Local settings: /home/transmute/project/transmute.toml
---------------------------------

[config]
debug = true
log_file = "transmute.log"
report = 2000

[pipeline]
do_not_add_drop = ["process_paths", "process_default_page"]
steps = ["collective.transmute.steps.ids.process_export_prefix", "collective.transmute.steps.ids.process_ids", "collective.transmute.steps.paths.process_paths", "collective.transmute.steps.portal_type.process_type", "collective.transmute.steps.basic_metadata.process_title", "collective.transmute.steps.basic_metadata.process_title_description", "collective.transmute.steps.review_state.process_review_state", "collective.transmute.steps.default_page.process_default_page", "collective.transmute.steps.image.process_image_to_preview_image_link", "collective.transmute.steps.data_override.process_data_override", "collective.transmute.steps.creators.process_creators", "collective.transmute.steps.constraints.process_constraints", "collective.transmute.steps.blocks.process_blocks", "collective.transmute.steps.blobs.process_blobs", "collective.transmute.steps.sanitize.process_cleanup"]

[principals]
remove = ["admin"]
default = "Plone"

[default_pages]
keys_from_parent = ["@id", "id"]
keep = false
```

If you don't have a {file}`transmute.toml` file, create one by running the following command.

```shell
uv run transmute settings generate
```


### `sanity`

This command runs a sanity check on the available steps for the pipeline.

```shell
uv run transmute sanity
```

```console
Sanity check for Pipeline Steps

 - collective.transmute.steps.ids.process_export_prefix: ✅
 - collective.transmute.steps.ids.process_ids: ✅
 - collective.transmute.steps.paths.process_paths: ✅
 - collective.transmute.steps.portal_type.process_type: ✅
 - collective.transmute.steps.basic_metadata.process_title_description: ✅
 - collective.transmute.steps.review_state.process_review_state: ✅
 - collective.transmute.steps.default_page.process_default_page: ✅
 - collective.transmute.steps.image.process_image_to_preview_image_link: ✅
 - collective.transmute.steps.data_override.process_data_override: ✅
 - collective.transmute.steps.creators.process_creators: ✅
 - collective.transmute.steps.constraints.process_constraints: ✅
 - collective.transmute.steps.blocks.process_blocks: ✅
 - collective.transmute.steps.blobs.process_blobs: ✅
 - collective.transmute.steps.sanitize.process_cleanup: ✅
Pipeline status: ✅
```
