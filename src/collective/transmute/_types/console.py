from collective.transmute import get_logger
from dataclasses import dataclass
from rich.console import Console

import logging
import os


__all__ = [
    "ConsoleArea",
    "ConsolePanel",
]


class ConsolePanel(Console):
    def __init__(self, *args, **kwargs):
        console_file = open(os.devnull, "w")  # noQA: SIM115
        super().__init__(*args, markup=True, record=True, file=console_file, **kwargs)

    def __rich_console__(self, console, options):
        texts = self.export_text(clear=False).split("\n")
        yield from texts[-options.height :]


@dataclass
class ConsoleArea:
    main: ConsolePanel
    side: ConsolePanel
    ui: bool = True
    _logger: logging.Logger | None = None

    @property
    def logger(self) -> logging.Logger:
        """Get the logger for the console area."""
        if self._logger is None:
            self._logger = get_logger()
        return self._logger

    def disable_ui(self):
        """Disable ui for the consoles."""
        self.ui = False
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        self.logger.addHandler(console)

    def print(self, message: str, panel_id: str = "main") -> None:
        """Print to one of the consoles."""
        if self.ui:
            console: ConsolePanel = getattr(self, panel_id)
            console.print(message)
        else:
            self.logger.info(message)

    def print_log(self, message: str, panel_id: str = "main") -> None:
        """Print to one of the consoles."""
        if self.ui:
            self.print(message, panel_id)
        self.logger.info(message)

    def debug(self, message: str, panel_id: str = "main") -> None:
        """Write a message to the debug logger."""
        self.logger.debug(message)
