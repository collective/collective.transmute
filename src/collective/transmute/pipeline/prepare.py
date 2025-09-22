from collective.transmute import _types as t
from collective.transmute.utils.pipeline import load_all_steps
from typing import cast


async def prepare_pipeline(
    state: t.PipelineState, settings: t.TransmuteSettings, consoles: t.ConsoleArea
) -> None:
    """
    Run all prepare steps for the pipeline.

    Args:
        state (PipelineState): The pipeline state object.
        settings (TransmuteSettings): The transmute settings object.
        consoles (ConsoleArea): Console logging utility.
    """
    pipeline_settings = settings.pipeline
    loader_steps = cast(
        tuple[t.PrepareStep, ...],
        load_all_steps(pipeline_settings.get("prepare_steps", ())),
    )
    for step in loader_steps:
        step_name = step.__name__
        consoles.debug(f"Running report step: {step_name}")
        async for status in step(state, settings):
            msg = "completed" if status else "failed"
        consoles.print(f"Loader step {step_name} run: {msg}")

    return None
