from collective.transmute import _types as t
from collective.transmute import get_logger
from dynaconf.loaders import toml_loader
from tempfile import NamedTemporaryFile

import typer


app = typer.Typer()


@app.command(name="settings")
def sanity(ctx: typer.Context) -> None:
    """Report settings to be used by this application."""
    logger = get_logger()
    logger.info("Settings used by this application")
    logger.info("")
    settings: t.TransmuteSettings = ctx.obj.settings
    data = settings._raw_data
    with NamedTemporaryFile(suffix=".toml", delete_on_close=False) as fp:
        filepath = fp.name
        toml_loader.write(filepath, data)
        response = fp.read().decode("utf-8")
    for line in response.split("\n"):
        logger.info(line)
