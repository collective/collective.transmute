---
myst:
  html_meta:
    "description": "How to create a custom pipeline step for collective.transmute"
    "property=og:description": "Learn how to write, register, and test custom pipeline steps for collective.transmute."
    "property=og:title": "Create a Pipeline Step | collective.transmute"
    "keywords": "Plone, collective.transmute, create, pipeline, step, guides, async, generator"
---

# Create a pipeline step

This guide explains how to create a custom pipeline step for {term}`collective.transmute`.
Pipeline steps are the building blocks of the transformation process.
Each step receives a content item, optionally transforms it, and yields the result.


## Step function signature

Every pipeline step must be an async generator function with the following signature.

```python
from collective.transmute import _types as t


async def my_step(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """Process an item in the pipeline."""
    # Transform the item
    yield item
```

The three parameters are always the same.

`item`
: The content item being processed, as a `PloneItem` dictionary.

`state`
: The pipeline state object, which holds progress counters, UID mappings, metadata, and annotations shared across all steps.

`settings`
: The transmute settings loaded from {file}`transmute.toml` and defaults.


## Yielding items

A step communicates its result by yielding.

### Keep the item

Yield the item (modified or not) to pass it to the next step.

```python
async def normalize_title(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """Normalize the title to title case."""
    title = item.get("title", "")
    if title:
        item["title"] = title.strip().title()
    yield item
```

### Drop the item

Yield `None` to remove the item from the pipeline.
The item will be recorded as "dropped" in the report, with the step name noted.

```python
async def drop_expired(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """Drop items that have an expiration date in the past."""
    expires = item.get("expires")
    if expires and expires < "2025-01-01T00:00:00":
        yield None
    else:
        yield item
```

### Yield multiple items

A step can yield more than one item.
This is useful when a single source item needs to be split into multiple destination items.
The pipeline will process each yielded item independently.

```{note}
When a step yields additional items beyond the first, they are counted as new items and increase the total item count in progress tracking.
```

```python
async def split_image(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """Extract an image from an item and yield it as a separate Image item."""
    image_data = item.get("image")
    if isinstance(image_data, dict):
        # Create a new Image item
        new_image = {
            "@id": f"{item['@id']}/image",
            "@type": "Image",
            "UID": "some-generated-uid",
            "id": "image",
            "title": item.get("title", ""),
            "image": image_data,
            "_is_new_item": True,
        }
        # Remove image from original item
        item.pop("image", None)
        # Yield the new item first, then the modified original
        yield new_image
        yield item
    else:
        yield item
```


## Reading configuration

Steps can read their own configuration from {file}`transmute.toml` via the `settings` parameter.

For example, given this configuration:

```toml
[steps.my_step]
threshold = 100
excluded_types = ["File", "Image"]
```

Access it in the step:

```python
async def my_step(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    step_config = settings.steps.get("my_step", {})
    threshold = step_config.get("threshold", 50)
    excluded = step_config.get("excluded_types", [])
    if item["@type"] in excluded:
        yield None
    else:
        yield item
```


## Using pipeline state

The `state` object provides shared context across all steps.

`state.metadata`
: The `MetadataInfo` object with relations, redirects, local roles, and other metadata collected during the prepare phase.

`state.uids`
: A dictionary mapping old UIDs to new UIDs.

`state.uid_path`
: A dictionary mapping UIDs to their destination paths.

`state.annotations`
: A dictionary for steps to share data with each other.

```python
async def track_languages(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """Track which languages are used across all items."""
    languages = state.annotations.setdefault("languages", set())
    lang = item.get("language", "")
    if lang:
        languages.add(lang)
    yield item
```


## Registering a step

To add your step to the pipeline, add its dotted Python path to the `pipeline.steps` list in {file}`transmute.toml`.

```toml
[pipeline]
steps = [
    "collective.transmute.steps.ids.process_export_prefix",
    "collective.transmute.steps.ids.process_ids",
    # ... other steps ...
    "my_package.steps.normalize_title",  # Your custom step
    "collective.transmute.steps.sanitize.process_cleanup",
]
```

```{important}
Step order matters.
Steps run sequentially from top to bottom.
Each step receives the item as modified by previous steps.
Place your step in the position that makes sense for your transformation logic.
```


### The `do_not_add_drop` setting

By default, the pipeline wraps each step so that if the step yields `None`, the item is recorded as "dropped" and removed from the pipeline.
Some steps need to yield `None` temporarily (for example, to defer processing) without marking the item as dropped.

If your step yields `None` for reasons other than dropping, add its function name to the `do_not_add_drop` list.

```toml
[pipeline]
do_not_add_drop = ["process_paths", "process_default_page", "my_deferred_step"]
```


## Testing a step

The project provides fixtures that make testing steps straightforward.
Tests are async and use `pytest` with `pytest-asyncio`.

```python
import pytest


@pytest.mark.parametrize(
    "base_item,expected_title",
    [
        [{"@id": "/foo", "@type": "Document", "UID": "abc", "id": "foo", "title": "hello world"}, "Hello World"],
        [{"@id": "/bar", "@type": "Document", "UID": "def", "id": "bar", "title": "  spaced  "}, "Spaced"],
    ],
)
async def test_normalize_title(
    pipeline_state, transmute_settings, base_item, expected_title
):
    from my_package.steps import normalize_title

    results = []
    async for item in normalize_title(base_item, pipeline_state, transmute_settings):
        results.append(item)
    assert len(results) == 1
    assert results[0]["title"] == expected_title
```

The `pipeline_state` and `transmute_settings` fixtures are provided by the test infrastructure in {file}`tests/conftest.py`.


## Complete example

The following is a complete, minimal step that filters items by a custom field read from configuration.

```python
"""Pipeline step to filter items by language."""
from collective.transmute import _types as t


async def filter_by_language(
    item: t.PloneItem,
    state: t.PipelineState,
    settings: t.TransmuteSettings,
) -> t.PloneItemGenerator:
    """Drop items whose language is not in the allowed list.

    Configuration in transmute.toml:

        [steps.language_filter]
        allowed = ["en", "de"]
    """
    step_config = settings.steps.get("language_filter", {})
    allowed = step_config.get("allowed", [])
    if not allowed or item.get("language", "") in allowed:
        yield item
    else:
        yield None
```

Register it in {file}`transmute.toml`.

```toml
[pipeline]
steps = [
    "collective.transmute.steps.ids.process_export_prefix",
    "collective.transmute.steps.ids.process_ids",
    "my_package.steps.filter_by_language",
    # ... remaining steps ...
]

[steps.language_filter]
allowed = ["en", "de"]
```
