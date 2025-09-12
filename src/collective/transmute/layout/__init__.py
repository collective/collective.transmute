from collective.transmute import _types as t
from collective.transmute.utils import sort_data
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.table import Table


class Header:
    """Display header."""

    def __init__(self, title: str):
        self.title = title

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row("[b]collective.transmute[/b]")
        grid.add_row(f"[b]{self.title}[/b]")
        return Panel(grid, style="white on blue")


class TransmuteReport:
    """Report Metadata info."""

    limit: int

    def __init__(self, data: dict[str, int], title: str, limit: int = 30):
        self.title = title
        self.data = data
        self.limit = limit

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=2)
        grid.add_column(justify="right", ratio=1)
        for name, total in sort_data(self.data):
            if len(name) > self.limit:
                idx = self.limit - 3
                name = name[:idx] + "..."
            grid.add_row(name, f"{total}")
        return Panel(grid, title=self.title, border_style="green")


def progress_panel(progress: t.PipelineProgress | t.ReportProgress) -> Panel:
    progress_table = Table.grid(expand=True)
    progress_table.add_row(progress.processed)
    if isinstance(progress, t.PipelineProgress):
        progress_table.add_row(progress.dropped)
    return Panel(
        progress_table,
        title="[b]Progress",
        border_style="green",
    )


def create_consoles() -> t.ConsoleArea:
    """Return a t.ConsoleArea object with two console objects."""
    main_console = t.ConsolePanel()
    side_console = t.ConsolePanel()
    return t.ConsoleArea(main_console, side_console)


class ApplicationLayout:
    title: str
    layout: Layout
    consoles: t.ConsoleArea
    progress: t.ReportProgress | t.PipelineProgress

    def __init__(self, title: str):
        self.consoles = create_consoles()
        self.layout = self._create_layout(title)
        self.title = title

    def _create_layout(self, title: str) -> Layout:
        return Layout(name="root")

    def update_layout(self, state: t.PipelineState | t.ReportState):
        pass

    def initialize_progress(self, total: int):
        pass


class TransmuteLayout(ApplicationLayout):
    def _create_layout(self, title: str) -> Layout:
        consoles = self.consoles
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", ratio=1),
            Layout(name="main", ratio=5),
            Layout(name="footer", ratio=1),
        )
        layout["main"].split_row(
            Layout(name="body", ratio=5, minimum_size=60),
            Layout(name="side", ratio=2),
        )
        layout["header"].update(Header(title=title))
        layout["body"].update(
            Panel(consoles.main, title="[b]Log", border_style="green"),
        )
        layout["side"].update(
            Panel("", title="[b]Report", border_style="green"),
        )
        layout["footer"].update(
            Panel("", title="[b]Progress", border_style="green"),
        )
        return layout

    def update_layout(self, state: t.PipelineState):
        """Update layout."""
        layout = self.layout
        layout["footer"].update(progress_panel(state.progress))
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_row(TransmuteReport(state.exported, "Transmuted"))
        grid.add_row(TransmuteReport(state.dropped, "Dropped"))
        layout["side"].update(
            Panel(
                grid,
                title="[b]Report",
                border_style="green",
            ),
        )

    def initialize_progress(self, total: int):
        processed = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            TextColumn(
                "[progress.percentage]{task.percentage:>3.0f}%[/progress.percentage] "
                "({task.completed}/{task.total})"
            ),
            expand=True,
        )
        dropped = Progress(
            "{task.description}",
            SpinnerColumn(),
            TextColumn("{task.completed}"),
        )
        processed_id = processed.add_task("[green]Processed", total=total)
        dropped_id = dropped.add_task("[red]Dropped")
        self.progress = t.PipelineProgress(processed, processed_id, dropped, dropped_id)


class ReportLayout(ApplicationLayout):
    def _create_layout(self, title: str) -> Layout:
        consoles = self.consoles
        layout = Layout(name="root")
        layout.split(
            Layout(name="header", ratio=1),
            Layout(name="main", ratio=4),
            Layout(name="body", ratio=2),
            Layout(name="footer", ratio=1),
        )
        layout["header"].update(Header(title=title))
        layout["body"].update(
            Panel(consoles.main, title="[b]Log", border_style="green"),
        )
        layout["main"].update(
            Panel("", title="[b]Report", border_style="green"),
        )
        layout["footer"].update(
            Panel("", title="[b]Progress", border_style="green"),
        )
        return layout

    def update_layout(self, state: t.ReportState):
        """Update layout."""
        layout = self.layout
        layout["footer"].update(progress_panel(state.progress))
        grid = Table.grid(expand=True)
        columns = ("Types", "States", "Creators", "Subjects")
        for _ in columns:
            grid.add_column(justify="left", ratio=1)

        row = []
        for name in columns:
            data = getattr(state, name.lower())
            row.append(TransmuteReport(data, name, limit=30))
        grid.add_row(*row)
        layout["main"].update(
            Panel(
                grid,
                title="[b]Report",
                border_style="green",
            ),
        )

    def initialize_progress(self, total: int):
        processed = Progress(
            "{task.description}",
            SpinnerColumn(),
            BarColumn(),
            TextColumn(
                "[progress.percentage]{task.percentage:>3.0f}%[/progress.percentage] "
                "({task.completed}/{task.total})"
            ),
            expand=True,
        )
        processed_id = processed.add_task("[green]Processed", total=total)
        self.progress = t.ReportProgress(processed, processed_id)


def live(app_layout: ApplicationLayout, redirect_stderr: bool = True) -> Live:
    """Return a rich.live.Live instance for a given layout."""
    return Live(
        app_layout.layout,
        refresh_per_second=10,
        screen=True,
        redirect_stderr=redirect_stderr,
    )
