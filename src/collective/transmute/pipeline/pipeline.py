from collections.abc import AsyncGenerator
from collective.transmute import _types as t
from collective.transmute.utils import item as item_utils
from contextlib import contextmanager


@contextmanager
def step_debugger(
    consoles: t.ConsoleArea, src_uid: str, item: t.PloneItem, step_name: str
):
    """Context manager to debug a step run."""
    consoles.debug(f"({src_uid}) - Step {step_name} - started")
    yield
    consoles.debug(f"({src_uid}) - Step {step_name} - finished")


def _add_to_drop(path: str, settings: t.TransmuteSettings) -> None:
    parents = item_utils.all_parents_for(path)
    valid_path = parents & settings.paths_filter_allowed
    if valid_path and not (parents & settings.paths["filter"]["drop"]):
        settings.paths["filter"]["drop"].add(path)


async def _sub_item_pipeline(
    steps: tuple[t.PipelineStep, ...],
    item: t.PloneItem,
    src_uid: str,
    step_name: str,
    state: t.PipelineState,
    consoles: t.ConsoleArea,
    settings: t.TransmuteSettings,
) -> AsyncGenerator[tuple[t.PloneItem | None, str, bool]]:
    msg = f" - New: {item.get('UID')} (from {src_uid}/{step_name})"
    consoles.print(msg)
    consoles.debug(f"({src_uid}) - Step {step_name} - Produced {item.get('UID')}")
    async for sub_item, last_step, _ in run_pipeline(
        steps, item, state, consoles, settings
    ):
        yield sub_item, last_step, True


async def run_step(
    steps: tuple[t.PipelineStep, ...],
    step: t.PipelineStep,
    item: t.PloneItem,
    src_uid: str,
    state: t.PipelineState,
    consoles: t.ConsoleArea,
    settings: t.TransmuteSettings,
) -> AsyncGenerator[tuple[t.PloneItem | None, str, bool]]:
    """Run a single step in the pipeline."""
    result_item: t.PloneItem | None = None
    step_name = step.__name__
    item_id, is_folderish = item["@id"], item.get("is_folderish", False)
    add_to_drop = step_name not in settings.do_not_add_drop
    async for result_item in step(item, state, settings):
        if not result_item:
            if is_folderish and add_to_drop:
                # Add this path to drop, to drop all children objects as well
                _add_to_drop(item_id, settings)
        elif result_item.pop("_is_new_item", False):
            async for sub_item, last_step, _ in _sub_item_pipeline(
                steps, result_item, src_uid, step_name, state, consoles, settings
            ):
                yield sub_item, last_step, True
    yield result_item, step_name, False


async def run_pipeline(
    steps: tuple[t.PipelineStep, ...],
    item: t.PloneItem | None,
    state: t.PipelineState,
    consoles: t.ConsoleArea,
    settings: t.TransmuteSettings,
) -> AsyncGenerator[tuple[t.PloneItem | None, str, bool]]:
    src_uid = item["UID"] if item else ""
    last_step_name = ""
    result_item: t.PloneItem | None = item
    for step in steps:
        step_name = step.__name__
        if not result_item:
            consoles.debug(f"({src_uid}) - Step {step_name} - skipped")
            continue
        with step_debugger(consoles, src_uid, result_item, step_name):
            async for sub_item, last_step, is_new in run_step(
                steps, step, result_item, src_uid, state, consoles, settings
            ):
                if is_new:
                    yield sub_item, last_step, True
                else:
                    result_item, last_step_name = sub_item, last_step
    yield result_item, last_step_name, False
