from collective.transmute import _types as t
from collective.transmute.settings.parse import get_default_settings
from collective.transmute.utils import settings as utils
from pathlib import Path

import tomlkit
import typer


app = typer.Typer()


def dump_settings(settings: t.TransmuteSettings) -> str:
    """Dump settings as TOML string."""
    data = settings._raw_data
    document = utils.settings_to_toml(data)
    return tomlkit.dumps(document)


@app.callback(invoke_without_command=True)
def settings(ctx: typer.Context) -> None:
    """Report settings to be used by this application."""
    if getattr(ctx, "obj", None) is None:
        # Check if we a have a subcommand (like 'generate')
        if ctx.invoked_subcommand != "generate":
            typer.echo("Did not find a transmute.toml file")
            typer.echo("You should first run 'uv run transmute generate'")
            raise typer.Exit(1) from None
        else:
            return

    msg = "Settings used by this application"
    typer.echo(msg)
    typer.echo("-" * len(msg))
    settings: t.TransmuteSettings = ctx.obj.settings
    config_file = settings.config["filepath"]
    local_settings = f"Local settings: {config_file}"
    typer.echo(local_settings)
    typer.echo("-" * len(local_settings))
    # Print settings
    for line in dump_settings(settings).split("\n"):
        typer.echo(line)


@app.command(name="generate")
def generate() -> None:
    """Generate a new ``transmute.toml`` settings file in the current directory."""
    settings = get_default_settings()
    data = dump_settings(settings)
    path = Path("transmute.toml").resolve()
    if path.exists():
        typer.echo(f"File already exists: {path}")
        raise typer.Exit(1) from None
    path.write_text(data, encoding="utf-8")
    typer.echo(f"Generated a settings file at {path}")
