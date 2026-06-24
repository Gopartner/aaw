import sys
import ctypes

from textual.app import App
from textual.binding import Binding

from aaw.screens import (
    HomeScreen,
    InstalledAppsScreen,
    AppDashboardScreen,
    LiveRuntimeScreen,
    APKCollectorScreen,
    RootDataCollectorScreen,
    AIWorkspaceScreen,
    WorkspaceExplorerScreen,
)


class AAW(App):
    TITLE = "Android Analysis Workspace"
    SUB_TITLE = "v1.0.0"

    CSS = """
    Screen {
        background: #11111b;
    }

    .panel-title {
        text-style: bold;
        color: #89b4fa;
        padding: 0 1;
    }

    .section-divider {
        color: #313244;
    }

    .value {
        color: #cdd6f4;
    }

    .label {
        color: #6c7086;
    }

    .dim {
        color: #585b70;
    }

    .screen-title {
        text-style: bold;
        color: #cdd6f4;
        background: #1e1e2e;
        border-bottom: solid #313244;
        padding: 1 2;
        text-align: center;
    }

    Input {
        background: #1e1e2e;
        border: round #45475a;
        color: #cdd6f4;
        padding: 0 1;
    }

    Input:focus {
        border: round #89b4fa;
    }

    ListView {
        background: #1e1e2e;
        border: round #313244;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: #313244;
    }

    ListView > ListItem:even {
        background: #1e1e2e;
    }

    ListView > ListItem:odd {
        background: #181825;
    }

    Button {
        background: #313244;
        color: #cdd6f4;
        border: round #45475a;
    }

    Button:hover {
        background: #45475a;
    }

    Button:focus {
        border: round #89b4fa;
    }

    ProgressBar {
        background: #313244;
        color: #a6e3a1;
    }

    ScrollableContainer {
        scrollbar-color: #45475a;
        scrollbar-size: 1 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("escape", "go_back", "Back"),
    ]

    SCREENS = {
        "home": HomeScreen,
        "installed_apps": InstalledAppsScreen,
        "app_dashboard": AppDashboardScreen,
        "live_runtime": LiveRuntimeScreen,
        "apk_collector": APKCollectorScreen,
        "root_data": RootDataCollectorScreen,
        "ai_workspace": AIWorkspaceScreen,
        "workspace_explorer": WorkspaceExplorerScreen,
    }

    def on_mount(self):
        self.push_screen("home")

    def action_go_back(self):
        if self.screen_stack:
            if len(self.screen_stack) <= 1:
                self.action_quit()
            else:
                self.pop_screen()

    def action_quit(self):
        self._restore_console()
        self.exit(return_code=0)

    @staticmethod
    def _restore_console():
        if sys.platform != "win32":
            return
        try:
            kernel32 = ctypes.windll.kernel32
            STD_INPUT_HANDLE = -10
            mode = 0x0001 | 0x0002 | 0x0004 | 0x0020 | 0x0040 | 0x0080
            kernel32.SetConsoleMode(kernel32.GetStdHandle(STD_INPUT_HANDLE), mode)
        except Exception:
            pass

    def navigate_to(self, screen_name: str, data=None):
        screen_class = self.SCREENS[screen_name]
        if data:
            screen = screen_class(data)
        else:
            screen = screen_class()
        self.push_screen(screen)

    def show_dashboard(self, app_data):
        self.navigate_to("app_dashboard", app_data)

    def show_live_runtime(self, app_data):
        self.navigate_to("live_runtime", app_data)

    def show_apk_collector(self, app_data):
        self.navigate_to("apk_collector", app_data)

    def show_root_data(self, app_data):
        self.navigate_to("root_data", app_data)

    def show_ai_workspace(self, app_data):
        self.navigate_to("ai_workspace", app_data)

    def show_workspace_explorer(self, _data=None):
        self.push_screen("workspace_explorer")
