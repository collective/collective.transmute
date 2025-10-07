from collective.transmute import _types as t
from collective.transmute.utils import files as file_utils
from pathlib import Path


async def write_paths_report(
    state: t.PipelineState, settings: t.TransmuteSettings, consoles: t.ConsoleArea
) -> t.ReportItemGenerator:
    """
    Write a CSV report of path transformations performed by the pipeline.

    Args:
        consoles (ConsoleArea): Console logging utility.
        state (PipelineState): The pipeline state object.

    Returns:
        Path to the report file.
    """
    headers = [
        "filename",
        "src_path",
        "src_uid",
        "src_type",
        "src_state",
        "dst_path",
        "dst_uid",
        "dst_type",
        "dst_state",
        "last_step",
        "status",
        "src_level",
        "dst_level",
        "src_workflow",
        "dst_workflow",
    ]
    if state.write_report:
        report_path = Path().cwd() / "report_transmute.csv"
        paths_data = state.path_transforms
        csv_path = await file_utils.csv_dump(paths_data, headers, report_path)
        consoles.print_log(f" - Wrote paths report to {csv_path}")
        yield report_path
    else:
        yield None
