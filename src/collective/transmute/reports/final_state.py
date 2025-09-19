from collective.transmute import _types as t
from collective.transmute.utils import sort_data_by_value


async def report_final_state(
    state: t.PipelineState, settings: t.TransmuteSettings, consoles: t.ConsoleArea
) -> t.ReportItemGenerator:
    """
    Print a summary of the pipeline's final state to the console.

    Args:
        consoles (ConsoleArea): Console logging utility.
        state (PipelineState): The pipeline state object.
        is_debug (bool): Whether to print the debug summary.

    """
    transmuted = len(state.seen)
    percent = (transmuted / state.total * 100) if state.total else 0
    consoles.print_log("Source")
    consoles.print_log(f"  - Processed items: {state.total}")
    consoles.print_log("Converted")
    consoles.print_log(f"  - Transmuted items: {transmuted} ({percent:.2f}%)")
    for name, total in sort_data_by_value(state.exported):
        percent = (total / transmuted * 100) if transmuted else 0
        consoles.print_log(f"   - {name}: {total} ({percent:.2f}%)")
    if settings.is_debug:
        consoles.print_log("Dropped by step")
        total_dropped = len(state.dropped)
        for name, total in sort_data_by_value(state.dropped):
            percent = (total / total_dropped * 100) if total_dropped else 0
            consoles.print_log(f"  - {name}: {total} ({percent:.2f}%)")
    yield None
