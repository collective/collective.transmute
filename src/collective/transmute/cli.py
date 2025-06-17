from collective.transmute._types import ContextObject
from collective.transmute.commands.report import app as app_report
from collective.transmute.commands.sanity import app as app_sanity
from collective.transmute.commands.settings import app as app_settings
from collective.transmute.commands.transmute import app as app_transmute
from collective.transmute.settings.parse import get_settings

import typer


app = typer.Typer(no_args_is_help=True)


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Welcome to transmute, the utility to transform data from
    collective.exportimport to plone.exportimport.
    """
    try:
        settings = get_settings()
    except RuntimeError:
        typer.echo("Did not find a repository.toml file.")
        raise typer.Exit() from None
    else:
        ctx_obj = ContextObject(settings=settings)
        ctx.obj = ctx_obj
        ctx.ensure_object(ContextObject)


app.add_typer(app_transmute)
app.add_typer(app_report)
app.add_typer(app_settings)
app.add_typer(app_sanity)


def cli():
    app()


__all__ = ["cli"]
