from textual.containers import Vertical, Horizontal
from textual.widgets import Static
from textual.binding import Binding
from textual.app import ComposeResult

from aaw.screens.base import BaseScreen
from aaw.widgets import ActionItem


class AppDashboardScreen(BaseScreen):
    BINDINGS = [
        Binding("1", "start_monitor", "Monitor"),
        Binding("2", "stop_monitor", "Stop"),
        Binding("3", "collect_apk", "APK"),
        Binding("4", "collect_data", "Data"),
        Binding("5", "screenshot", "SS"),
        Binding("6", "generate_report", "Report"),
        Binding("7", "generate_ai", "AI"),
        Binding("8", "open_output", "Output"),
        Binding("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    AppDashboardScreen #content-area {
        align: center top;
    }

    #dash-wrap {
        width: 72;
        height: auto;
        margin: 1 2;
    }

    #dash-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 1;
        text-align: center;
    }

    .dash-title {
        text-style: bold;
        color: #cdd6f4;
    }

    .dash-pkg {
        color: #585b70;
    }

    #info-panel, #runtime-panel, #actions-panel {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
        padding: 0 1;
    }

    .dl { color: #6c7086; }
    .dv { color: #cdd6f4; }
    .dg { color: #a6e3a1; }
    .dy { color: #f9e2af; }
    .dr { color: #f38ba8; }

    .action-row {
        padding: 0 1;
    }

    """

    def __init__(self, app_data: dict):
        super().__init__()
        self.app_data = app_data

    def body(self) -> ComposeResult:
        a = self.app_data
        with Vertical(id="dash-wrap"):
            with Vertical(id="dash-header"):
                yield Static(f"  {a['name']}", classes="dash-title")
                yield Static(f"  [#585b70]{a['package']}[/]", classes="dash-pkg")

            with Vertical(id="info-panel"):
                yield Static("  [#585b70]INFO[/]", classes="panel-title")
                yield Static("")
                for label, val, cls in [
                    ("Version", a["version"], "dv"),
                    ("UID", a["uid"], "dv"),
                    ("Target SDK", str(a["target_sdk"]), "dv"),
                    ("Root Access", a["root_access"], "dg" if a["root_access"] == "YES" else "dr"),
                ]:
                    yield Horizontal(Static(f"  {label:14}", classes="dl"), Static(f" {val}", classes=cls))
                yield Static("")

            with Vertical(id="runtime-panel"):
                yield Static("  [#585b70]RUNTIME[/]", classes="panel-title")
                yield Static("")
                yield Horizontal(Static("  Status          ", classes="dl"), Static(" RUNNING ", classes="dg"))
                yield Horizontal(Static("  Activity        ", classes="dl"), Static(" HomeActivity", classes="dy"))
                yield Horizontal(Static("  Running Time    ", classes="dl"), Static(" 00:08:22", classes="dv"))
                yield Static("")

            with Vertical(id="actions-panel"):
                yield Static("  [#585b70]ACTIONS[/]", classes="panel-title")
                yield Static("")
                for k, d, a in [("1", "Start Monitor", "start_monitor"), ("2", "Stop Monitor", "stop_monitor"),
                                ("3", "Collect APK", "collect_apk"), ("4", "Collect Data", "collect_data"),
                                ("5", "Screenshot", "screenshot"), ("6", "Generate Report", "generate_report"),
                                ("7", "AI Workspace", "generate_ai"), ("8", "Open Output", "open_output")]:
                    yield ActionItem(k, d, action=a)
                yield Static("")

    def action_start_monitor(self):
        self.app.show_live_runtime(self.app_data)

    def action_stop_monitor(self):
        pass

    def action_collect_apk(self):
        self.app.show_apk_collector(self.app_data)

    def action_collect_data(self):
        self.app.show_root_data(self.app_data)

    def action_screenshot(self):
        pass

    def action_generate_report(self):
        pass

    def action_generate_ai(self):
        self.app.show_ai_workspace(self.app_data)

    def action_open_output(self):
        self.app.show_workspace_explorer()

    def on_action_item_selected(self, event: ActionItem.Selected):
        action = event.item.action
        method = getattr(self, f"action_{action}", None)
        if method:
            method()
