from collective.transmute import _types as t
from contextlib import contextmanager
from datetime import datetime
from functools import cache
from importlib import import_module


@cache
def load_step(name: str) -> t.PipelineStep:
    """Load a step from a dotted name."""
    mod_name, func_name = name.rsplit(".", 1)
    try:
        mod = import_module(mod_name)
    except ModuleNotFoundError:
        raise RuntimeError(f"Function {name} not available") from None
    func = getattr(mod, func_name, None)
    if not func:
        raise RuntimeError(f"Function {name} not available") from None
    return func


def load_all_steps(names: tuple[str]) -> tuple[t.PipelineStep]:
    steps = []
    for name in names:
        steps.append(load_step(name))
    return tuple(steps)


def check_steps(names: tuple[str]) -> list[tuple[str, bool]]:
    steps: list[tuple[str, bool]] = []
    for name in names:
        status = True
        try:
            load_step(name)
        except RuntimeError:
            status = False
        steps.append((name, status))
    return steps


def load_processor(type_: str, settings: t.TransmuteSettings) -> t.ItemProcessor:
    """Load a processor for a given type."""
    types_config = settings.types
    name = types_config.get(type_, {}).get("processor")
    if not name:
        name = types_config.get("processor", "")
    mod_name, func_name = name.rsplit(".", 1)
    try:
        mod = import_module(mod_name)
    except ModuleNotFoundError:
        raise RuntimeError(f"Function {name} not available") from None
    func = getattr(mod, func_name, None)
    if not func:
        raise RuntimeError(f"Function {name} not available") from None
    return func


def sort_data(
    data: dict[str, int], reverse: bool = True
) -> tuple[tuple[str, int], ...]:
    return tuple(sorted(data.items(), key=lambda x: x[1], reverse=reverse))


@contextmanager
def report_time(title: str, consoles: t.ConsoleArea):
    start = datetime.now()
    msg = f"{title} started at {start}"
    consoles.print_log(msg)
    yield
    finish = datetime.now()
    msg = f"{title} ended at {finish}\n{title} took {(finish - start).seconds} seconds"
    consoles.print_log(msg)
