from collective.transmute import _types as t

import tomlkit
import typer


app = typer.Typer()


@app.command(name="settings")
def sanity(ctx: typer.Context) -> None:
    """Report settings to be used by this application."""
    msg = "Settings used by this application"
    typer.echo(msg)
    typer.echo("-" * len(msg))
    settings: t.TransmuteSettings = ctx.obj.settings
    config_file = settings.config["filepath"]
    typer.echo(f"Local settings: {config_file}")
    typer.echo("-" * len(msg))
    data = settings._raw_data
    response = tomlkit.dumps(data)
    for line in response.split("\n"):
        typer.echo(line)
