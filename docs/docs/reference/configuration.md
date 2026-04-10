---
myst:
  html_meta:
    "description": "Complete reference of all transmute.toml configuration options for collective.transmute"
    "property=og:description": "Detailed reference for every section and key in the transmute.toml configuration file."
    "property=og:title": "Configuration Reference | collective.transmute"
    "keywords": "Plone, collective.transmute, configuration, TOML, transmute.toml, reference, settings"
---

# Configuration reference

This page documents every section and key available in the {file}`transmute.toml` configuration file.

To generate an initial configuration file with defaults, run the following command.

```shell
uv run transmute settings generate
```

```{seealso}
For an introduction to configuring migrations, see {doc}`/how-to-guides/usage`.
```


## `[config]`

General application settings.

```toml
[config]
debug = false
log_file = "transmute.log"
prepare_data_location = "."
reports_location = "."
report = 1000
```

`debug`
: Enable debug mode. When `true`, additional logging is written.
  Default: `false`

`log_file`
: Path to the log file.
  Default: `"transmute.log"`

`prepare_data_location`
: Directory where prepared metadata files are stored during processing.
  Default: `"."`

`reports_location`
: Directory where generated report files are saved.
  Default: `"."`

`report`
: Number of items processed between progress updates in the log.
  Default: `1000`

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.settings`
  - `logger_settings()`
  - `log_file`
* - {py:mod}`collective.transmute.reports`
  - `get_reports_location()`
  - `reports_location`
* - {py:mod}`collective.transmute.commands.report`
  - `report()`
  - `reports_location`
* - {py:mod}`collective.transmute.reports.final_state`
  - `report_final_state()`
  - `debug`
```


## `[pipeline]`

Controls which steps run and in what order.

```toml
[pipeline]
prepare_steps = []
steps = [
    "collective.transmute.steps.ids.process_export_prefix",
    "collective.transmute.steps.uids.drop_item_by_uid",
    "collective.transmute.steps.dates.filter_by_date",
    "collective.transmute.steps.ids.process_ids",
    "collective.transmute.steps.paths.process_paths",
    "collective.transmute.steps.portal_type.process_type",
    "collective.transmute.steps.basic_metadata.process_title",
    "collective.transmute.steps.basic_metadata.process_title_description",
    "collective.transmute.steps.review_state.process_review_state",
    "collective.transmute.steps.default_page.process_default_page",
    "collective.transmute.steps.image.process_image_to_preview_image_link",
    "collective.transmute.steps.data_override.process_data_override",
    "collective.transmute.steps.creators.process_creators",
    "collective.transmute.steps.constraints.process_constraints",
    "collective.transmute.steps.blocks.process_blocks",
    "collective.transmute.steps.blobs.process_blobs",
    "collective.transmute.steps.sanitize.process_cleanup",
]
report_steps = [
    "collective.transmute.reports.paths.write_paths_report",
    "collective.transmute.reports.final_state.report_final_state",
    "collective.transmute.reports.dropped.report_dropped_by_path_prefix",
]
do_not_add_drop = ["process_paths", "process_default_page"]
```

`prepare_steps`
: List of dotted paths to functions that run before the main pipeline.
  These steps prepare metadata (for example, redirects, local roles, and relations).
  Default: `[]`

`steps`
: Ordered list of dotted paths to pipeline step functions.
  Each step is an async generator that receives and yields items.
  See {doc}`/how-to-guides/create_step` for details on writing custom steps.

`report_steps`
: List of dotted paths to functions that run after the pipeline completes.
  These generate CSV reports and console summaries.

`do_not_add_drop`
: List of step function names (not full dotted paths) that should not be wrapped with the automatic drop-item logic.
  Use this for steps that yield `None` for reasons other than dropping an item.
  Default: `["process_paths", "process_default_page"]`

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.pipeline`
  - `all_steps()`
  - `steps`
* - {py:mod}`collective.transmute.pipeline.prepare`
  - `prepare_pipeline()`
  - `prepare_steps`
* - {py:mod}`collective.transmute.pipeline.report`
  - `final_reports()`
  - `report_steps`
* - {py:mod}`collective.transmute.pipeline.pipeline`
  - `run_step()`
  - `do_not_add_drop`
* - {py:mod}`collective.transmute.commands.sanity`
  - `sanity()`
  - `steps`
```


## `[site_root]`

Defines the source and destination site root paths, used for path rewriting and redirect generation.

```toml
[site_root]
src = "/Plone"
dest = "/Plone"
```

`src`
: The site root path in the source (exported) data.
  Default: `"/Plone"`

`dest`
: The site root path in the destination portal.
  Default: `"/Plone"`

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.pipeline`
  - `pipeline()`
  - `dest`
* - {py:mod}`collective.transmute.steps.portal_type.collection`
  - `_src_site_root()`
  - `src`
```


## `[principals]`

Controls how content creators are processed.

```toml
[principals]
default = "Plone"
remove = ["admin"]
```

`default`
: The default creator to use when all original creators are removed.
  Default: `"Plone"`

`remove`
: List of creator usernames to remove from content items.
  Default: `["admin"]`

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.steps.creators`
  - `process_creators()`
  - `remove`, `default`
```


## `[default_pages]`

Controls how default pages (index pages) are handled during migration.

```toml
[default_pages]
keep = false
keys_from_parent = ["@id", "id"]
```

`keep`
: Whether to keep default pages as separate items.
  When `false`, the default page is merged into its parent container.
  Default: `false`

`keys_from_parent`
: List of keys to copy from the parent item when merging a default page.
  Default: `["@id", "id"]`

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.steps.default_page`
  - `process_default_page()`
  - `keep`, `keys_from_parent`
```


## `[review_state]`

Controls filtering and rewriting of workflow review states.

### `[review_state.filter]`

```toml
[review_state.filter]
allowed = ["published"]
```

`allowed`
: List of review states to keep. Items in other states are dropped.
  An empty list allows all states.
  Default: `["published"]`

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.review_state`
  - `process_review_state()`
```

### `[review_state.rewrite]`

```toml
[review_state.rewrite]
states = {}
workflows = {}
```

`states`
: Mapping of source review state names to destination review state names.
  Default: `{}`

`workflows`
: Mapping of source workflow IDs to destination workflow IDs.
  Default: `{}`

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.utils.workflow`
  - `rewrite_workflow_history()`
```


## `[paths]`

Controls path processing, filtering, and cleanup.

```toml
[paths]
export_prefixes = ["http://localhost:8080/Plone"]
```

`export_prefixes`
: List of URL prefixes to strip from item `@id` values.
  These are the base URLs of the source Plone site.
  Default: `["http://localhost:8080/Plone"]`

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.ids`
  - `process_export_prefix()`
```

### `[paths.cleanup]`

Mapping of path substrings to their replacements.

```toml
[paths.cleanup]
"/_" = "/"
```

Each key is a substring to find in item paths, and the value is its replacement.

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.ids`
  - `process_ids()`
```

### `[paths.filter]`

```toml
[paths.filter]
allowed = []
drop = []
```

`allowed`
: List of path prefixes to keep. If not empty, only items under these prefixes are processed.
  An empty list allows all paths.
  Default: `[]`

`drop`
: List of path prefixes to exclude. Items under these prefixes are dropped.
  Default: `[]`

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.paths`
  - `process_paths()`
```

### `[paths.portal_type]`

Mapping of path prefixes to portal type overrides.
Items under a given path prefix will have their portal type changed.

```toml
[paths.portal_type]
"/news" = "News Item"
```

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.portal_type`
  - `process_type()`
```


## `[images]`

Controls image-to-preview-image conversion.

```toml
[images]
to_preview_image_link = []
```

`to_preview_image_link`
: List of portal types whose `image` field should be extracted into a separate Image item with a `preview_image_link` relation.
  Default: `[]`

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.steps.image`
  - `process_image_to_preview_image_link()`
  - `to_preview_image_link`
```


## `[sanitize]`

Controls which fields are removed from items at the end of the pipeline.

```toml
[sanitize]
drop_keys = [
    "is_folderish",
    "items",
    "layout",
    "limit",
    "lock",
    "nextPreviousEnabled",
    "parent",
]
block_keys = [
    "item_count",
    "items_total",
    "limit",
    "query",
    "sort_on",
    "sort_reversed",
    "text",
    "template_layout",
    "tiles",
]
```

`drop_keys`
: List of keys to remove from all items.

`block_keys`
: List of additional keys to remove from items that have Volto blocks.
  These keys are typically remnants of the classic Plone content model and are no longer needed once the content has been converted to blocks.

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.steps.sanitize`
  - `process_cleanup()`
  - `drop_keys`, `block_keys`
```


## `[data_override]`

Path-based field overrides. Each key is an item path, and the value is a dictionary of fields to set on that item.

```toml
[data_override]
"/some/specific/path" = { "title" = "New Title", "review_state" = "private" }
```

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.steps.data_override`
  - `process_data_override()`
  - Item `@id` lookup
```


## `[types]`

Defines portal type mappings, processors, and block configurations.

### Global processor

```toml
[types]
processor = "collective.transmute.steps.portal_type.default.processor"
```

`processor`
: Dotted path to the default type processor function.
  Used for types that don't define their own processor.

### Per-type configuration

Each portal type can have its own subsection.

```toml
[types.Document]
portal_type = "Document"
blocks = [{ "@type" = "title" }, { "@type" = "description" }]

[types.Folder]
portal_type = "Document"

[types.Collection]
portal_type = "Document"
processor = "collective.transmute.steps.portal_type.collection.processor"
```

`portal_type`
: The destination portal type. Use this to map source types to different destination types (for example, `Folder` to `Document`).

`processor`
: Dotted path to a type-specific processor function. Overrides the global processor for this type.

`blocks`
: List of default Volto blocks to add to items of this type.
  Each block is a dictionary with at least an `@type` key.

`override_blocks`
: Alternative block list that takes precedence over `blocks` when present.

```{list-table} Used by
:header-rows: 1
:widths: 50 30 20

* - Module
  - Function
  - Keys
* - {py:mod}`collective.transmute.steps.portal_type`
  - `process_type()`
  - `portal_type`, `processor`
* - {py:mod}`collective.transmute.steps.blocks`
  - `process_blocks()`
  - `blocks`, `override_blocks`
* - {py:mod}`collective.transmute.steps.constraints`
  - `process_constraints()`
  - `portal_type`
* - {py:mod}`collective.transmute.utils.portal_types`
  - `fix_portal_type()`
  - `portal_type`
```


## `[steps]`

Per-step configuration. Each step can define its own subsection under `[steps]`.

### `[steps.blocks.variations]`

Mapping of classic Plone view names to Volto listing block variations.

```toml
[steps.blocks.variations]
listing_view = "listing"
summary_view = "summary"
tabular_view = "listing"
full_view = "summary"
album_view = "imageGallery"
```

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.blocks`
  - `process_blocks()`
```

### `[steps.blobs]`

```toml
[steps.blobs]
field_names = ["file", "image", "preview_image"]
```

`field_names`
: List of field names that contain blob data to be extracted as separate files.

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.blobs`
  - `process_blobs()`
```

### `[steps.date_filter]`

Date thresholds for filtering items. Items with field values older than the threshold are dropped.

```toml
[steps.date_filter]
created = "2000-01-01T00:00:00"
```

Each key is a date field name, and the value is the ISO 8601 date threshold.

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.dates`
  - `filter_by_date()`
```

### `[steps.paths.prefix_replacement]`

Mapping of source path prefixes to destination path prefixes for path rewriting.

```toml
[steps.paths.prefix_replacement]
"/old-section" = "/new-section"
```

```{list-table} Used by
:header-rows: 1
:widths: 60 40

* - Module
  - Function
* - {py:mod}`collective.transmute.steps.ids`
  - `process_ids()`
```
