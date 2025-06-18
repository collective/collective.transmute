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
    """Context manager to debug the processing of a pipeline."""
    consoles.debug(f"Starting pipeline processing of {state.total} items")
    yield consoles.debug
    consoles.debug(f"Finished pipeline processing of {state.total} items")


def all_steps(settings: t.TransmuteSettings) -> tuple[t.PipelineStep, ...]:
    """Return all steps for this pipeline."""
    config_steps = settings.pipeline.get("steps")
    return load_all_steps(config_steps)


def _prepare_report_items(
    item: t.PloneItem | None, last_step: str, is_new: bool, src_item: dict
) -> tuple[dict, dict]:
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
    metadata._data_files_ = [i[1] for i in state.paths]
    metadata_file = await file_utils.export_metadata(
        metadata, state, consoles, settings
    )
    return metadata_file


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
                steps, raw_item, metadata, consoles, settings
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
                paths.append((item["@id"], data_file))
                metadata._blob_files_.extend(item_files.blob_files)
                item_uid = item["UID"]
                exported[item["@type"]] += 1
                seen.add(item_uid)
                uids[item_uid] = item_uid
                # Map the old_uid to the new uid
                if old_uid := item.pop("_UID", None):
                    uids[old_uid] = item_uid

    # Reports after pipeline execution
    await report.final_reports(consoles, state, write_report, settings.is_debug)
    # Write metadata file
    metadata_file = await _write_metadata(metadata, state, consoles, settings)
    return metadata_file
