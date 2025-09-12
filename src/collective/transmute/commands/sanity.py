from collective.transmute import _types as t
from collective.transmute.utils import check_steps

import typer


app = typer.Typer()


@app.command()
def sanity(ctx: typer.Context) -> None:
    """Run a sanity check on pipeline steps."""
    typer.echo("Sanity check for Pipeline Steps")
    typer.echo("")
    pipeline_status = True
    settings: t.TransmuteSettings = ctx.obj.settings
    for name, status in check_steps(settings.pipeline["steps"]):
        pipeline_status = pipeline_status and status
        status_check = "✅" if status else "❗"
        typer.echo(f" - {name}: {status_check}")
    status_check = "✅" if pipeline_status else "❗"
    typer.echo(f"Pipeline status: {status_check}")
