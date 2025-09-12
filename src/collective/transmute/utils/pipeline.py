"""
Pipeline utilities for collective.transmute.

This module provides helper functions for loading pipeline steps and processors
by dotted names, checking step availability, and managing step configuration in the
transformation pipeline. Functions are documented for Sphinx autodoc and support
pipeline extensibility and dynamic loading.
"""

from collective.transmute import _types as t
from functools import cache
from importlib import import_module


@cache
def load_step(name: str) -> t.PipelineStep:
    """
    Load a pipeline step function from a dotted name.

    Parameters
    ----------
    name : str
        The dotted name of the function (e.g., 'module.submodule.func').

    Returns
    -------
    PipelineStep
        The loaded pipeline step function.

    Raises
    ------
    RuntimeError
        If the module or function cannot be found.

    Example
    -------
    >>> step = load_step('my_module.my_step')
    """
    mod_name, func_name = name.rsplit(".", 1)
    try:
        mod = import_module(mod_name)
    except ModuleNotFoundError:
        raise RuntimeError(f"Function {name} not available") from None

    if not (func := getattr(mod, func_name, None)):
        raise RuntimeError(f"Function {name} not available") from None
    return func


def load_all_steps(names: tuple[str, ...]) -> tuple[t.PipelineStep, ...]:
    """
    Load all pipeline step functions from a tuple of dotted names.

    Parameters
    ----------
    names : tuple[str, ...]
        Tuple of dotted function names.

    Returns
    -------
    tuple[PipelineStep, ...]
        Tuple of loaded pipeline step functions.
    """
    steps = []
    for name in names:
        steps.append(load_step(name))
    return tuple(steps)


def check_steps(names: tuple[str, ...]) -> list[tuple[str, bool]]:
    """
    Check if pipeline step functions can be loaded from dotted names.

    Parameters
    ----------
    names : tuple[str, ...]
        Tuple of dotted function names.

    Returns
    -------
    list[tuple[str, bool]]
        List of (name, status) tuples indicating if each step is available.
    """
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
    """
    Load a processor function for a given type from settings.

    Parameters
    ----------
    type_ : str
        The type for which to load the processor.
    settings : TransmuteSettings
        The transmute settings object containing processor configuration.

    Returns
    -------
    ItemProcessor
        The loaded processor function.

    Raises
    ------
    RuntimeError
        If the processor function cannot be found.
    """
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
