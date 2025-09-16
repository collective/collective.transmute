from collective.transmute import _types as t
from collective.transmute.utils import sort_data_by_value
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TextColumn
from rich.table import Table


class Header:
    """
    Display a header panel for the application.

    Parameters
    ----------
    title : str
        The title to display in the header.

    Example
    -------
    .. code-block:: pycon

        >>> header = Header("My Title")
        >>> panel = header.__rich__()
    """

    def __init__(self, title: str):
        self.title = title

    def __rich__(self) -> Panel:
        """
        Render the header as a Rich Panel.

        Returns
        -------
        Panel
            A Rich Panel object displaying the header.
        """
        grid = Table.grid(expand=True)
        grid.add_column(justify="center", ratio=1)
        grid.add_row("[b]collective.transmute[/b]")
        grid.add_row(f"[b]{self.title}[/b]")
        return Panel(grid, style="white on blue")


class TransmuteReport:
    """
    Display a report panel with metadata information.

    Parameters
    ----------
    data : dict[str, int]
        The data to display in the report.
    title : str
        The title of the report panel.
    limit : int, optional
        Maximum length for item names (default: 30).

    Example
    -------
    .. code-block:: pycon

        >>> report = TransmuteReport({'TypeA': 10, 'TypeB': 5}, 'Exported')
        >>> panel = report.__rich__()
    """

    limit: int

    def __init__(self, data: dict[str, int], title: str, limit: int = 30):
        self.title = title
        self.data = data
        self.limit = limit

    def __rich__(self) -> Panel:
        """
        Render the report as a Rich Panel.

        Returns
        -------
        Panel
            A Rich Panel object displaying the report.
        """
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=2)
        grid.add_column(justify="right", ratio=1)
        for name, total in sort_data_by_value(self.data):
            if len(name) > self.limit:
                idx = self.limit - 3
                name = name[:idx] + "..."
            grid.add_row(name, f"{total}")
        return Panel(grid, title=self.title, border_style="green")


def progress_panel(progress: t.PipelineProgress | t.ReportProgress) -> Panel:
    """
    Create a progress panel for the current pipeline or report progress.

    Parameters
    ----------
    progress : PipelineProgress or ReportProgress
        The progress object to display.

    Returns
    -------
    Panel
        A Rich Panel object showing progress.
    """
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
    """
    Create a ``ConsoleArea`` object with two console panels.

    Returns
    -------
    ConsoleArea
        An object containing main and side consoles.

    Example
    -------
    .. code-block:: pycon

        >>> consoles = create_consoles()
    """
    main_console = t.ConsolePanel()
    side_console = t.ConsolePanel()
    return t.ConsoleArea(main_console, side_console)


class ApplicationLayout:
    """
    Base layout for the application.

    Parameters
    ----------
    title : str
        The title for the layout.

    Attributes
    ----------
    title : str
        The layout title.
    layout : Layout
        The Rich Layout object.
    consoles : ConsoleArea
        The console area for logs and side info.
    progress : ReportProgress or PipelineProgress
        The progress bar object.

    Example
    -------
    .. code-block:: pycon

        >>> layout = ApplicationLayout('My App')
    """

    title: str
    layout: Layout
    consoles: t.ConsoleArea
    progress: t.ReportProgress | t.PipelineProgress

    def __init__(self, title: str):
        self.consoles = create_consoles()
        self.layout = self._create_layout(title)
        self.title = title

    def _create_layout(self, title: str) -> Layout:
        """
        Create the Rich Layout for the application.

        Parameters
        ----------
        title : str
            The title for the layout.

        Returns
        -------
        Layout
            The Rich Layout object.
        """
        return Layout(name="root")

    def update_layout(self, state: t.PipelineState | t.ReportState) -> None:
        """
        Update the layout with the current state.

        Parameters
        ----------
        state : PipelineState or ReportState
            The state object containing progress and report data.
        """
        pass

    def initialize_progress(self, total: int) -> None:
        """
        Initialize the progress bar.

        Parameters
        ----------
        total : int
            The total number of items to process.
        """
        pass


class TransmuteLayout(ApplicationLayout):
    """
    Layout for the transmute pipeline application.

    Example
    -------
    .. code-block:: pycon

        >>> layout = TransmuteLayout('Transmute')
    """

    def _create_layout(self, title: str) -> Layout:
        """
        Create the layout for the transmute pipeline.

        Parameters
        ----------
        title : str
            The title for the layout.

        Returns
        -------
        Layout
            The Rich Layout object.
        """
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

    def update_layout(self, state: t.PipelineState) -> None:
        """
        Update the layout with the pipeline state.

        Parameters
        ----------
        state : PipelineState
            The pipeline state object.
        """
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

    def initialize_progress(self, total: int) -> None:
        """
        Initialize the progress bar for the pipeline.

        Parameters
        ----------
        total : int
            The total number of items to process.
        """
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
    """
    Layout for displaying report information.

    Example
    -------
    .. code-block:: pycon

        >>> layout = ReportLayout('Report')
    """

    def _create_layout(self, title: str) -> Layout:
        """
        Create the layout for the report.

        Parameters
        ----------
        title : str
            The title for the layout.

        Returns
        -------
        Layout
            The Rich Layout object.
        """
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

    def update_layout(self, state: t.ReportState) -> None:
        """
        Update the layout with the report state.

        Parameters
        ----------
        state : ReportState
            The report state object.
        """
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

    def initialize_progress(self, total: int) -> None:
        """
        Initialize the progress bar for the report.

        Parameters
        ----------
        total : int
            The total number of items to process.
        """
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
    """
    Create a Rich Live instance for the given application layout.

    Parameters
    ----------
    app_layout : ApplicationLayout
        The application layout to display.
    redirect_stderr : bool, optional
        Whether to redirect stderr to the live display (default: ``True``).

    Returns
    -------
    Live
        A Rich Live instance for the layout.

    Example
    -------
    .. code-block:: pycon

        >>> live_display = live(layout)
    """
    return Live(
        app_layout.layout,
        refresh_per_second=10,
        screen=True,
        redirect_stderr=redirect_stderr,
    )
