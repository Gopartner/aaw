from textual.containers import Vertical, Horizontal
from textual.widgets import Static
from textual.binding import Binding
from textual.app import ComposeResult

from aaw.data import MOCK_WORKSPACE_ITEMS
from aaw.screens.base import BaseScreen


class AIWorkspaceScreen(BaseScreen):
    BINDINGS = [
        Binding("g", "generate", "Generate"),
        Binding("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    AIWorkspaceScreen #content-area {
        align: center top;
    }

    #ai-wrap {
        width: 74;
        height: auto;
        margin: 1 2;
    }

    #ai-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #progress-list, #status-panel, #location-panel {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        margin: 1 0 0 0;
        padding: 0 1;
    }

    .ai-label { color: #6c7086; }

    """

    def __init__(self, app_data: dict):
        super().__init__()
        self.app_data = app_data

    def body(self) -> ComposeResult:
        with Vertical(id="ai-wrap"):
            yield Static(" AI Workspace Generator ", id="ai-header")

            with Vertical(id="progress-list"):
                yield Static("")
                yield Static("  [#585b70]GENERATING[/]", classes="panel-title")
                yield Static("")
                for item in MOCK_WORKSPACE_ITEMS:
                    yield Static(f"  [#a6e3a1]✔[/] {item}")
                yield Static("")

            with Vertical(id="status-panel"):
                yield Static("")
                yield Horizontal(Static("  AI Ready        ", classes="ai-label"), Static(" [#a6e3a1]YES[/]"))
                yield Horizontal(Static("  Dev Ready       ", classes="ai-label"), Static(" [#a6e3a1]YES[/]"))
                yield Static("")

            with Vertical(id="location-panel"):
                yield Static("")
                yield Static("  [#585b70]LOCATION[/]", classes="panel-title")
                yield Static("")
                for line in ["output/", "  WhatsApp/", "    com.whatsapp/",
                             "      10-15-22_kamis-25-06-2026/"]:
                    yield Static(f"  [#89b4fa]{line}[/]")
                yield Static("")

    def action_generate(self):
        pass
