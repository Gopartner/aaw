from textual.containers import Vertical, Horizontal
from textual.widgets import Static
from textual.binding import Binding
from textual.app import ComposeResult

from aaw.data import MOCK_TIMELINE
from aaw.screens.base import BaseScreen


class LiveRuntimeScreen(BaseScreen):
    BINDINGS = [
        Binding("space", "toggle_pause", "Pause"),
        Binding("s", "screenshot", "Screenshot"),
        Binding("e", "export_log", "Export"),
        Binding("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    LiveRuntimeScreen #content-area {
        align: center top;
    }

    #rt-wrap {
        width: 74;
        height: auto;
        margin: 1 2;
    }

    #rt-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #current-panel, #timeline-panel, #stats-panel, #rt-footer {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
        padding: 0 1;
    }

    #timeline-panel {
        height: 14;
        overflow-y: auto;
    }

    .rl { color: #6c7086; }
    .rv { color: #cdd6f4; }
    .ra { color: #f9e2af; }

    .footer-text {
        color: #585b70;
    }

    """

    def __init__(self, app_data: dict):
        super().__init__()
        self.app_data = app_data

    def body(self) -> ComposeResult:
        with Vertical(id="rt-wrap"):
            yield Static(" Runtime Activity Monitor ", id="rt-header")

            with Vertical(id="current-panel"):
                yield Static("  [#585b70]CURRENT[/]", classes="panel-title")
                yield Static("")
                yield Horizontal(Static("  Activity   ", classes="rl"), Static(" HomeActivity", classes="ra"))
                yield Horizontal(Static("  Package    ", classes="rl"), Static(f" {self.app_data['package']}", classes="rv"))
                yield Horizontal(Static("  Started    ", classes="rl"), Static(" 10:12:41", classes="rv"))
                yield Horizontal(Static("  Duration   ", classes="rl"), Static(" 00:01:22", classes="rv"))
                yield Static("")

            with Vertical(id="timeline-panel"):
                yield Static("  [#585b70]TIMELINE[/]", classes="panel-title")
                yield Static("")
                for e in MOCK_TIMELINE:
                    yield Static(f"  [#89b4fa]{e['time']}[/]  {e['activity']}")
                yield Static("")

            with Vertical(id="stats-panel"):
                yield Static("")
                yield Horizontal(Static("  Events          ", classes="rl"), Static(str(len(MOCK_TIMELINE)), classes="rv"))
                acts = len(set(e["activity"] for e in MOCK_TIMELINE))
                yield Horizontal(Static("  Unique Acts     ", classes="rl"), Static(str(acts), classes="rv"))
                yield Horizontal(Static("  Transitions     ", classes="rl"), Static(str(len(MOCK_TIMELINE) - 1), classes="rv"))
                yield Static("")

            with Vertical(id="rt-footer"):
                yield Static(" [#f38ba8]SPACE[/] Pause  [#f38ba8]S[/] Screenshot  [#f38ba8]E[/] Export  [#f38ba8]Q[/] Exit", classes="footer-text")

    def action_toggle_pause(self):
        pass

    def action_screenshot(self):
        pass

    def action_export_log(self):
        pass
