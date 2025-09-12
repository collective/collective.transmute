"""
Pipeline reporting steps for collective.transmute.

This module provides functions to generate and print reports about the
pipeline's final state and path transformations. Used for logging and CSV
export in the collective.transmute pipeline.

Example:
    >>> await final_reports(consoles, state, write_report=True, is_debug=True)
"""
from collective.transmute import _types as t
from collective.transmute.utils import files as file_utils
from collective.transmute.utils import sort_data_by_value
from pathlib import Path


async def report_final_state(consoles: t.ConsoleArea, state: t.PipelineState) -> None:
    """
    Print a summary of the pipeline's final state to the console.

    Args:
        consoles (ConsoleArea): Console logging utility.
        state (PipelineState): The pipeline state object.

    Returns:
        None

    Example:
        >>> await report_final_state(consoles, state)
    """
    consoles.print_log("Converted")
    consoles.print_log(f"  - Total: {len(state.seen)}")
    for name, total in sort_data_by_value(state.exported):
        consoles.print_log(f"   - {name}: {total}")
    consoles.print_log("Dropped by step")
    for name, total in sort_data_by_value(state.dropped):
        consoles.print_log(f"  - {name}: {total}")


async def write_paths_report(
    consoles: t.ConsoleArea,
    state: t.PipelineState,
):
    """
    Write a CSV report of path transformations performed by the pipeline.

    Args:
        consoles (ConsoleArea): Console logging utility.
        state (PipelineState): The pipeline state object.

    Returns:
        None

    Example:
        >>> await write_paths_report(consoles, state)
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
    ]
    report_path = Path().cwd() / "report_transmute.csv"
    paths_data = state.path_transforms
    csv_path = await file_utils.csv_dump(paths_data, headers, report_path)
    consoles.print_log(f" - Wrote paths report to {csv_path}")


async def final_reports(
    consoles: t.ConsoleArea, state: t.PipelineState, write_report: bool, is_debug: bool
) -> None:
    """
    Run final reporting steps for the pipeline, including CSV export and
    console summary.

    Args:
        consoles (ConsoleArea): Console logging utility.
        state (PipelineState): The pipeline state object.
        write_report (bool): Whether to write the CSV report.
        is_debug (bool): Whether to print the debug summary.

    Returns:
        None

    Example:
        >>> await final_reports(consoles, state, write_report=True, is_debug=True)
    """
    if write_report:
        await write_paths_report(consoles, state)
    if is_debug:
        await report_final_state(consoles, state)
