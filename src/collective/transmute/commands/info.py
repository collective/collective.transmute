import typer


app = typer.Typer()


def blocks_report(converter: dict) -> list[str]:
    """
    Describe each Volto block type and the state the settings give it.

    :param converter: The ``[steps.blocks.converter]`` table of the settings.
    :returns: One line per block type, sorted by block type.
    """
    from collective.html2blocks.registry import report_blocks
    from collective.html2blocks.registry import resolve_blocks

    enabled = resolve_blocks(converter).enabled
    lines = []
    for row in report_blocks():
        name = row["block_type"]
        state = "enabled" if name in enabled else "disabled"
        source = "transmute.toml" if name in converter else "default"
        lines.append(f" - {name}: {state} ({source}), package: {row['package']}")
    return lines


@app.callback(invoke_without_command=True)
def info(ctx: typer.Context) -> None:
    """
    Show information about the ``collective.transmute`` tool and its main dependencies.
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
    typer.echo("")
    typer.echo("Volto blocks:")
    settings = getattr(ctx.obj, "settings", None)
    converter = (
        settings.steps.get("blocks", {}).get("converter", {}) if settings else {}
    )
    for line in blocks_report(converter):
        typer.echo(line)
