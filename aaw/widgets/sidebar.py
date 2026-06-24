from textual.containers import Vertical, Horizontal
from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from textual.binding import Binding

from aaw.utils import is_adb_available


NAV_ITEMS = [
    ("home",         " 01 ", "Home"),
    ("installed_apps"," 02 ", "Apps"),
    ("app_dashboard"," 03 ", "Dashboard"),
    ("live_runtime", " 04 ", "Monitor"),
    ("apk_collector"," 05 ", "APK Tool"),
    ("root_data",    " 06 ", "Root Data"),
    ("ai_workspace", " 07 ", "AI Workspace"),
    ("workspace_explorer","08 ", "Explorer"),
]

SCREEN_LABEL = {
    "home": "Home",
    "installed_apps": "Installed Apps",
    "app_dashboard": "App Dashboard",
    "live_runtime": "Runtime Monitor",
    "apk_collector": "APK Tool",
    "root_data": "Root Data",
    "ai_workspace": "AI Workspace",
    "workspace_explorer": "Workspace",
}


class SidebarItem(Static):
    def __init__(self, screen_name: str, num: str, label: str, active: bool = False):
        super().__init__()
        self.screen_name = screen_name
        self.num = num
        self.label = label
        self.active = active

    def on_mount(self):
        self._refresh()

    def set_active(self, active: bool):
        self.active = active
        self._refresh()

    def _refresh(self):
        if self.active:
            self.update(
                f"  [bold #89b4fa]▸[/] [bold #cdd6f4]{self.num}[/] [#89b4fa]{self.label}[/]"
            )
        else:
            self.update(
                f"    [#585b70]{self.num}[/] [#a6adc8]{self.label}[/]"
            )


class Sidebar(Static):
    current_screen = reactive("home")

    def watch_current_screen(self, old: str, new: str):
        for child in self.query(SidebarItem):
            child.set_active(child.screen_name == new)
        self._update_bottom()

    def compose(self):
        yield Static("", classes="sidebar-spacer")
        yield Static("  [bold #89b4fa]AAW[/] [#585b70]v1.0.0[/]", id="sidebar-logo")
        yield Static("", classes="sidebar-spacer")
        yield Static("  [#585b70]NAVIGATION[/]", classes="sidebar-section")
        yield Static("", classes="sidebar-spacer")
        for i, (name, num, label) in enumerate(NAV_ITEMS):
            item = SidebarItem(name, num, label, active=(name == "home"))
            yield item
        yield Static("", classes="sidebar-spacer")
        yield Static("  [#585b70]STATUS[/]", classes="sidebar-section")
        yield Static("", classes="sidebar-spacer")
        yield Static("  [dim]Device:[/]", id="sb-device-label")
        yield Static("  [dim]ADB:[/]", id="sb-adb-label")
        yield Static("", classes="sidebar-spacer sidebar-bottom")
        yield Static("  [dim]refresh: 5s[/]", id="sb-refresh")
        yield Static("  [dim]q quit[/]", id="sb-quit")

    def on_mount(self):
        self._check_adb()

    def _update_bottom(self):
        pass

    def _check_adb(self):
        try:
            ok = is_adb_available()
        except Exception:
            ok = False
        adb_label = self.query_one("#sb-adb-label", Static)
        device_label = self.query_one("#sb-device-label", Static)
        if ok:
            adb_label.update("  [green]ADB:[/] [#a6e3a1]Connected[/]")
            device_label.update("  [dim]Device:[/] [#cdd6f4]ready[/]")
        else:
            adb_label.update("  [red]ADB:[/] [#f38ba8]Offline[/]")
            device_label.update("  [dim]Device:[/] [#f38ba8]none[/]")
