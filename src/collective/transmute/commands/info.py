import typer


app = typer.Typer()


@app.callback(invoke_without_command=True)
def info() -> None:
    """
    Show information about the collective.transmute tool and its main dependencies.
    """
    from collective.html2blocks import __version__ as html2blocks_version
    from collective.transmute import PACKAGE_NAME
    from collective.transmute import __version__

    package_info = f"{PACKAGE_NAME} - {__version__}"
    typer.echo(f"{package_info}")
    typer.echo("=" * len(package_info))
    typer.echo("")
    typer.echo("Dependencies:")
    typer.echo(f" - collective.html2blocks: {html2blocks_version}")
