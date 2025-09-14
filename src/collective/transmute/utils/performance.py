"""
Performance utilities for ``collective.transmute``.

This module provides context managers and helpers for timing and reporting
performance metrics during the transformation pipeline. Functions are documented
for Sphinx autodoc and support logging execution times.
"""

from collective.transmute import _types as t
from contextlib import contextmanager
from datetime import datetime


@contextmanager
def report_time(title: str, consoles: t.ConsoleArea):
    """
    Context manager to report the start and end time of a process.

    Parameters
    ----------
    title : str
        The title or label for the timed process.
    consoles : ConsoleArea
        The console area for logging messages.

    Example
    -------
    >>> with report_time('Step 1', consoles):
    ...     # code to time
    """
    start = datetime.now()
    msg = f"{title} started at {start}"
    consoles.print_log(msg)
    yield
    finish = datetime.now()
    msg = f"{title} ended at {finish}\n{title} took {(finish - start).seconds} seconds"
    consoles.print_log(msg)
