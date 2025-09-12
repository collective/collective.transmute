"""
CLI entry point for ``collective.transmute``.

This module provides the Typer-based command-line interface for converting
data from collective.exportimport to plone.exportimport.

Example:
    .. code-block:: shell

        uv run transmute settings
        uv run transmute sanity
"""

from collective.transmute._types import ContextObject
from collective.transmute.commands.info import app as app_info
from collective.transmute.commands.report import app as app_report
from collective.transmute.commands.sanity import app as app_sanity
from collective.transmute.commands.settings import app as app_settings
from collective.transmute.commands.transmute import app as app_transmute
from collective.transmute.settings.parse import get_settings

import typer


app = typer.Typer(no_args_is_help=True)

SUBCOMMANDS_IGNORE_SETTINGS = {"info", "settings"}


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Welcome to transmute, the utility to transform data from
    collective.exportimport to plone.exportimport.
    """
    # Always add a line
    typer.echo("")
    try:
        settings = get_settings()
    except (RuntimeError, FileNotFoundError):
        if ctx.invoked_subcommand not in SUBCOMMANDS_IGNORE_SETTINGS:
            typer.echo("Did not find a transmute.toml file.")
            raise typer.Exit(1) from None
        else:
            return
    else:
        ctx_obj = ContextObject(settings=settings)
        ctx.obj = ctx_obj
        ctx.ensure_object(ContextObject)


app.add_typer(app_info, name="info")
app.add_typer(app_transmute)
app.add_typer(app_report)
app.add_typer(app_settings, name="settings")
app.add_typer(app_sanity)


def cli():
    app()


__all__ = ["cli"]
