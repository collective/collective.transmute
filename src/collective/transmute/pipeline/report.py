from collective.transmute import _types as t
from collective.transmute.utils import files as file_utils
from collective.transmute.utils import sort_data
from pathlib import Path


async def report_final_state(consoles: t.ConsoleArea, state: t.PipelineState) -> None:
    consoles.print_log("Converted")
    consoles.print_log(f"  - Total: {len(state.seen)}")
    for name, total in sort_data(state.exported):
        consoles.print_log(f"   - {name}: {total}")
    consoles.print_log("Dropped by step")
    for name, total in sort_data(state.dropped):
        consoles.print_log(f"  - {name}: {total}")


async def write_paths_report(
    consoles: t.ConsoleArea,
    state: t.PipelineState,
):
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
    if write_report:
        await write_paths_report(consoles, state)
    if is_debug:
        await report_final_state(consoles, state)
