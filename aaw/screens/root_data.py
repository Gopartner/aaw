from textual.containers import Vertical, Horizontal
from textual.widgets import Static, ProgressBar
from textual.binding import Binding
from textual.app import ComposeResult

from aaw.data import MOCK_DATA_COLLECT
from aaw.screens.base import BaseScreen


class RootDataCollectorScreen(BaseScreen):
    BINDINGS = [
        Binding("c", "collect", "Collect"),
        Binding("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    RootDataCollectorScreen #content-area {
        align: center top;
    }

    #root-wrap {
        width: 74;
        height: auto;
        margin: 1 2;
    }

    #root-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #collect-list, #progress-panel, #save-panel {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        margin: 1 0 0 0;
        padding: 0 1;
    }

    .cl { color: #6c7086; }
    .cv { color: #cdd6f4; }

    ProgressBar {
        width: 100%;
        background: #313244;
        color: #a6e3a1;
    }

    """

    def __init__(self, app_data: dict):
        super().__init__()
        self.app_data = app_data

    def body(self) -> ComposeResult:
        with Vertical(id="root-wrap"):
            yield Static(" Root Data Collection ", id="root-header")

            with Vertical(id="collect-list"):
                yield Static("")
                yield Static("  [#585b70]COLLECT[/]", classes="panel-title")
                yield Static("")
                for item in MOCK_DATA_COLLECT:
                    yield Static(f"  [#a6e3a1]✔[/] {item}")
                yield Static("")

            with Vertical(id="progress-panel"):
                yield Static("")
                yield Static("  [#585b70]PROGRESS[/]", classes="panel-title")
                yield Static("")
                yield ProgressBar(total=100, progress=100, show_percentage=False)
                yield Static("")
                yield Static("  [#a6e3a1]100%[/]", classes="value")
                yield Static("")

            with Vertical(id="save-panel"):
                yield Static("")
                yield Static("  [#585b70]SAVED[/]", classes="panel-title")
                yield Static("")
                for line in ["output/", "  WhatsApp/", "    com.whatsapp/",
                             "      10-15-22_kamis-25-06-2026/", "        data/"]:
                    yield Static(f"  [#89b4fa]{line}[/]")
                yield Static("")

    def action_collect(self):
        pass
