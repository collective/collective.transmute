from collections import defaultdict
from collective.transmute import _types as t
from collective.transmute import layout
from collective.transmute.pipeline import pipeline
from collective.transmute.utils import files as file_utils
from collective.transmute.utils import report_time
from pathlib import Path
from typing import Annotated

import asyncio
import typer


app = typer.Typer()


def _create_state(
    app_layout: layout.ApplicationLayout,
    total: int,
    metadata: t.MetadataInfo | None = None,
    write_report: bool = True,
) -> t.PipelineState:
    """Initialize a PipelineState object."""
    app_layout.initialize_progress(total)
    return t.PipelineState(
        total,
        processed=0,
        exported=defaultdict(int),
        dropped=defaultdict(int),
        progress=app_layout.progress,
        metadata=metadata,
        write_report=write_report,
    )


def _remove_existing_data(dst: Path, consoles: t.ConsoleArea):
    consoles.print_log(f"Removing existing content in {dst}")
    file_utils.remove_data(dst, consoles)


def _run_pipeline(
    src: Path,
    dst: Path,
    app_layout: layout.TransmuteLayout,
    consoles: t.ConsoleArea,
    clean_up: bool,
    write_report: bool,
    settings: t.TransmuteSettings,
):
    consoles.print(f"Listing content in {src}")
    src_files = file_utils.get_src_files(src)
    total = len(src_files.content)
    consoles.print(f"- Found {total} files to be processed")
    if clean_up:
        _remove_existing_data(dst, consoles)
    state = _create_state(app_layout, total, write_report=write_report)
    app_layout.update_layout(state)
    with report_time("Transmute", consoles):
        asyncio.run(pipeline(src_files, dst, state, consoles, settings))


@app.command()
def run(
    ctx: typer.Context,
    src: Annotated[Path, typer.Argument(help="Source path of the migration")],
    dst: Annotated[Path, typer.Argument(help="Destination path of the migration")],
    write_report: Annotated[
        bool,
        typer.Option(
            help="Should we write a CSV report with all path transformations?"
        ),
    ] = False,
    clean_up: Annotated[
        bool,
        typer.Option(help="Should we remove all existing files in the dst?"),
    ] = False,
    ui: Annotated[
        bool,
        typer.Option(help="Use rich UI"),
    ] = True,
):
    """Transmutes data from ``src`` folder (in ``collective.exportimport`` format)
    to ``plone.exportimport`` format in the ``dst`` folder.
    """
    settings: t.TransmuteSettings = ctx.obj.settings
    # Check if paths exist
    file_utils.check_paths(src, dst)
    app_layout = layout.TransmuteLayout(title=f"{src} -> {dst}")
    consoles = app_layout.consoles
    if ui:
        with layout.live(app_layout, redirect_stderr=False):
            _run_pipeline(
                src, dst, app_layout, consoles, clean_up, write_report, settings
            )
    else:
        consoles.disable_ui()
        _run_pipeline(src, dst, app_layout, consoles, clean_up, write_report, settings)
