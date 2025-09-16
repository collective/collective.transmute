"""
Pipeline initialization and orchestration for ``collective.transmute``.

This module provides functions and context managers to run, debug, and manage
pipeline steps for Plone item transformation. Used in the ``collective.transmute``
pipeline.

Example:
    .. code-block:: python

        >>> metadata_file = await pipeline(
        ...        src_files, dst, state, True, consoles, settings
        ... )
"""

from collections.abc import Callable
from collective.transmute import _types as t
from collective.transmute.pipeline import report
from collective.transmute.pipeline.pipeline import run_pipeline
from collective.transmute.settings import get_settings
from collective.transmute.utils import exportimport as ei_utils
from collective.transmute.utils import files as file_utils
from collective.transmute.utils import load_all_steps
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def pipeline_debugger(
    consoles: t.ConsoleArea,
    state: t.PipelineState,
):
    """
    Context manager to debug the processing of a pipeline.

    Args:
        consoles (ConsoleArea): Console logging utility.
        state (PipelineState): The pipeline state object.

    Example:
        .. code-block:: python

            >>> with pipeline_debugger(consoles, state) as dbg:
            ...     dbg("Debug message")
    """
    consoles.debug(f"Starting pipeline processing of {state.total} items")
    yield consoles.debug
    consoles.debug(f"Finished pipeline processing of {state.total} items")


def all_steps(settings: t.TransmuteSettings) -> tuple[t.PipelineStep, ...]:
    """
    Return all steps for this pipeline.

    Args:
        settings (TransmuteSettings): The transmute settings object.

    Returns:
        tuple[PipelineStep, ...]: All pipeline steps.

    Example:
        .. code-block:: python

            >>> steps = all_steps(settings)
    """
    config_steps = settings.pipeline.get("steps")
    return load_all_steps(config_steps)


def _prepare_report_items(
    item: t.PloneItem | None, last_step: str, is_new: bool, src_item: dict
) -> tuple[dict, dict]:
    """
    Prepare source and destination report items for pipeline reporting.

    Args:
        item (PloneItem | None): The processed item.
        last_step (str): The last step name.
        is_new (bool): Whether the item is new.
        src_item (dict): The source item dictionary.

    Returns:
        tuple[dict, dict]: Source and destination report items.

    Example:
        .. code-block:: python

            >>> src, dst = _prepare_report_items(item, last_step, is_new, src_item)
    """
    if not item:
        return src_item, {
            "dst_path": "--",
            "dst_type": "--",
            "dst_uid": "--",
            "dst_state": "--",
            "last_step": last_step,
        }
    dst_item = {
        "dst_path": item.get("@id", "") or "",
        "dst_type": item.get("@type", "") or "",
        "dst_uid": item.get("UID", "") or "",
        "dst_state": item.get("review_state", "--") or "--",
    }
    if is_new:
        src_item["src_type"] = "--"
        src_item["src_uid"] = "--"
        src_item["src_state"] = "--"
    return src_item, dst_item


async def _write_metadata(
    metadata: t.MetadataInfo,
    state: t.PipelineState,
    consoles: t.ConsoleArea,
    settings: t.TransmuteSettings,
):
    # Sort data files according to path
    state.paths.sort()
    metadata._data_files_ = [i[-1] for i in state.paths]
    metadata_file = await file_utils.export_metadata(
        metadata, state, consoles, settings
    )
    return metadata_file


async def post_process(
    state: t.PipelineState,
    consoles: t.ConsoleArea,
    content_folder: Path,
    settings: t.TransmuteSettings,
    debugger: Callable,
):
    metadata = state.metadata
    if not metadata:
        consoles.debug("No metadata found, skipping post-processing")
        return
    total_post_processing = len(state.post_processing)
    consoles.debug(
        f"Starting pipeline post-processing of {total_post_processing} items"
    )
    # Process uids
    uids = []
    for uid in state.post_processing:
        if uid in state.uids:
            uids.append(state.uids[uid])
        else:
            consoles.debug(f"UID {uid} not found in state.uids")
    # Get data paths
    content_files = [
        content_folder / path for _, uid, path in state.paths if uid in uids
    ]
    # Process
    async for _, raw_item in file_utils.json_reader(content_files):
        uid = raw_item["UID"]
        data_folder = content_folder / uid
        steps_names = tuple(state.post_processing[uid])
        steps = load_all_steps(steps_names)
        async for item, last_step, is_new in run_pipeline(
            steps, raw_item, state, consoles, settings
        ):
            if not item:
                # Dropped item, we need to remove it
                file_utils.remove_data(data_folder, consoles)
                debugger(f"Item {uid} dropped during post-processing")
                continue
            item_files = await file_utils.export_item(item, content_folder)
            if is_new:
                # This should not happen, but just in case we log it
                debugger(f"New item found during post-processing: {item.get('UID')}")
                data_file = item_files.data
                metadata._blob_files_.extend(item_files.blob_files)
                state.paths.append((item["@id"], item["UID"], data_file))
            debugger(f"Post-processing: Item {uid} last step {last_step}")


async def pipeline(
    src_files: t.SourceFiles,
    dst: Path,
    state: t.PipelineState,
    write_report: bool,
    consoles: t.ConsoleArea,
    settings: t.TransmuteSettings | None = None,
):
    if not settings:
        settings = get_settings()
    content_folder = dst / "content"
    metadata: t.MetadataInfo = await ei_utils.initialize_metadata(
        src_files, content_folder
    )
    # Add metadata to the state
    state.metadata = metadata
    steps: tuple[t.PipelineStep, ...] = all_steps(settings)
    content_files: list[Path] = src_files.content
    # Pipeline state variables
    total = state.total
    processed = state.processed
    exported = state.exported
    dropped = state.dropped
    progress = state.progress
    seen = state.seen
    uids = state.uids
    uid_path = state.uid_path
    path_transforms = state.path_transforms
    paths = state.paths
    consoles.debug(f"Starting pipeline processing of {state.total} items")
    with pipeline_debugger(consoles, state) as debugger:
        async for filename, raw_item in file_utils.json_reader(content_files):
            src_item = {
                "filename": filename,
                "src_path": raw_item.get("@id"),
                "src_type": raw_item.get("@type"),
                "src_uid": raw_item.get("UID"),
                "src_state": raw_item.get("review_state", "--"),
            }
            debugger(
                f"({src_item['src_uid']}) - Filename {src_item['filename']} "
                f"({processed + 1} / {total})"
            )
            async for item, last_step, is_new in run_pipeline(
                steps, raw_item, state, consoles, settings
            ):
                processed += 1
                progress.advance("processed")
                src_item["src_path"] = raw_item.get("_@id", src_item["src_path"])
                src_item, dst_item = _prepare_report_items(
                    item, last_step, is_new, src_item
                )
                if not item:
                    # Dropped file
                    progress.advance("dropped")
                    dropped[last_step] += 1
                    path_transforms.append(t.PipelineItemReport(**src_item, **dst_item))
                    continue
                elif is_new:
                    total += 1
                    progress.total("processed", total)

                path_transforms.append(t.PipelineItemReport(**src_item, **dst_item))
                item_files = await file_utils.export_item(item, content_folder)
                # Update metadata
                data_file = item_files.data
                metadata._blob_files_.extend(item_files.blob_files)
                item_path = item["@id"]
                item_uid = item["UID"]
                exported[item["@type"]] += 1
                seen.add(item_uid)
                uids[item_uid] = item_uid
                uid_path[item_uid] = item_path
                paths.append((item_path, item_uid, data_file))
                # Map the old_uid to the new uid
                if old_uid := item.pop("_UID", None):
                    uids[old_uid] = item_uid
                    uid_path[old_uid] = item_path
                    if post_steps := state.post_processing.pop(old_uid, None):
                        state.post_processing[item_uid] = post_steps

        if state.post_processing:
            await post_process(state, consoles, content_folder, settings, debugger)

    # Reports after pipeline execution
    await report.final_reports(consoles, state, write_report, settings.is_debug)
    # Write metadata file
    metadata_file = await _write_metadata(metadata, state, consoles, settings)
    return metadata_file
