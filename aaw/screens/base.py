from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static, Footer
from textual.binding import Binding

from aaw.widgets import Sidebar

SIDEBAR_MIN_WIDTH = 110


class ContentArea(Vertical):
    pass


class BaseScreen(Screen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("f1", "toggle_sidebar", "Sidebar"),
    ]

    DEFAULT_CSS = """
    BaseScreen > Horizontal {
        width: 100%;
        height: 100%;
    }

    #content-area {
        width: 1fr;
        height: 100%;
        background: #181825;
        overflow-y: auto;
    }

    #sidebar-container {
        width: 22;
        height: 100%;
        border-left: solid #313244;
        background: #11111b;
    }

    Header {
        background: #181825;
        color: #cdd6f4;
        border-bottom: solid #313244;
        text-style: bold;
    }

    Footer {
        background: #11111b;
        color: #585b70;
        border-top: solid #313244;
    }
    """

    def compose(self):
        with Horizontal():
            with ContentArea(id="content-area"):
                yield Static(id="screen-header", classes="screen-title")
                yield from self.body()
            with Vertical(id="sidebar-container"):
                yield Sidebar(id="app-sidebar")
        yield Footer()

    def body(self):
        yield Static("Content")

    def on_mount(self):
        sb = self.query_one(Sidebar)
        screen_key = self._screen_key()
        if screen_key:
            sb.current_screen = screen_key
        self._update_sidebar()

    def on_resize(self):
        self._update_sidebar()

    def _update_sidebar(self):
        sb = self.query_one("#sidebar-container")
        if sb:
            width = self.app.size.width if hasattr(self.app, 'size') else 999
            sb.display = width >= SIDEBAR_MIN_WIDTH

    def _screen_key(self):
        name = type(self).__name__
        mapping = {
            "HomeScreen": "home",
            "InstalledAppsScreen": "installed_apps",
            "AppDashboardScreen": "app_dashboard",
            "LiveRuntimeScreen": "live_runtime",
            "APKCollectorScreen": "apk_collector",
            "RootDataCollectorScreen": "root_data",
            "AIWorkspaceScreen": "ai_workspace",
            "WorkspaceExplorerScreen": "workspace_explorer",
        }
        return mapping.get(name)

    def action_toggle_sidebar(self):
        sb = self.query_one("#sidebar-container")
        if sb:
            sb.display = not sb.display

    def action_go_back(self):
        if len(self.app.screen_stack) > 1:
            self.app.pop_screen()

    def notify_info(self, message: str):
        self.app.notify(message, timeout=3)

    def notify_error(self, message: str):
        self.app.notify(message, severity="error", timeout=5)

    def notify_success(self, message: str):
        self.app.notify(message, severity="success", timeout=3)

    def notify_warning(self, message: str):
        self.app.notify(message, severity="warning", timeout=4)
