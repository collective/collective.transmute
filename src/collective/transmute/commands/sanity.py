from collective.transmute import _types as t
from collective.transmute import get_logger
from collective.transmute.utils import check_steps

import typer


app = typer.Typer()


@app.command()
def sanity(ctx: typer.Context) -> None:
    """Run a sanity check on pipeline steps."""
    logger = get_logger()
    logger.info("Pipeline Steps")
    logger.info("")
    pipeline_status = True
    settings: t.TransmuteSettings = ctx.obj.settings
    for name, status in check_steps(settings.pipeline["steps"]):
        pipeline_status = pipeline_status and status
        status_check = "✅" if status else "❗"
        logger.info(f" - {name}: {status_check}")
    status_check = "✅" if pipeline_status else "❗"
    logger.info(f"Pipeline status: {status_check}")
