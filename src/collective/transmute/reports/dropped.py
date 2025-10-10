from collective.transmute import _types as t
from collective.transmute.reports import get_reports_location
from collective.transmute.utils import files as file_utils
from typing import cast


async def report_dropped_by_path_prefix(
    state: t.PipelineState, settings: t.TransmuteSettings, consoles: t.ConsoleArea
) -> t.ReportItemGenerator:
    """Report total items dropped due to a path prefix."""
    consoles.print_log("Preparing dropped by path prefix report...")
    annotations = state.annotations.get(
        "dropped_by_path_prefix", cast(dict[str, int], {})
    )
    dropped_by_path_prefix: list[tuple[str, int]] = sorted(
        annotations.items(), key=lambda x: x[1], reverse=True
    )
    base_path = get_reports_location(settings)
    report_path = base_path / "report_dropped_by_path.csv"
    data = [{"path": path, "count": count} for path, count in dropped_by_path_prefix]
    csv_path = await file_utils.csv_dump(data, ["path", "count"], report_path)
    consoles.print_log(f" - Wrote dropped report to {csv_path}")
    yield report_path
