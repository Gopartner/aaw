from textual.containers import Vertical
from textual.widgets import Static, Input
from textual.binding import Binding
from textual.reactive import reactive
from textual.app import ComposeResult

from aaw.screens.base import BaseScreen
from aaw.utils import get_device_info, is_adb_available
from aaw.widgets import MenuItem

LOGO = """
   █████╗  █████╗ ██╗    ██╗
  ██╔══██╗██╔══██╗██║    ██║
  ███████║███████║██║ █╗ ██║
  ██╔══██║██╔══██║██║███╗██║
  ██║  ██║██║  ██║╚███╔███╔╝
  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚══╝╚══╝
"""


class DevicePanel(Static):
    device_info = reactive({}, init=False)

    def compose(self):
        yield Static("  [#585b70]DEVICE[/]", classes="panel-title")
        yield Static("")
        yield Static("    [#6c7086]checking...[/]", id="dv-model")
        yield Static("")

    def watch_device_info(self, info):
        def _fmt(val, default="-"):
            return val if val and val.strip() else default

        if not info or not info.get("connected"):
            self.remove_children()
            self.mount_all([
                Static("  [#585b70]DEVICE[/]", classes="panel-title"),
                Static(""),
                Static("    [#585b70]no device detected[/]  "),
                Static("    [#f38ba8]ADB disconnected[/]     "),
                Static(""),
            ])
        else:
            model = _fmt(info.get("model"), "Unknown")
            ver = _fmt(info.get("android_version"), "?")
            root = "[#a6e3a1]YES[/]" if info.get("root") else "[#f38ba8]NO[/]"
            status = "[#a6e3a1]Connected[/]"
            if info.get("serial") and "unauthorized" in str(info.get("serial", "")):
                status = "[#f9e2af]Unauthorized[/]"

            self.remove_children()
            self.mount_all([
                Static("  [#585b70]DEVICE[/]", classes="panel-title"),
                Static(""),
                Static(f"    {model:25}", classes="value"),
                Static(f"    Android {ver:20}", classes="value"),
                Static(f"    Root   : {root:<16}", classes="value"),
                Static(f"    ADB    : {status:<16}", classes="value"),
                Static(""),
            ])


class HomeScreen(BaseScreen):
    BINDINGS = [
        Binding("1", "go('installed_apps')", "Apps"),
        Binding("2", "go('installed_apps')", "Analyze"),
        Binding("3", "go('installed_apps')", "APK"),
        Binding("4", "go('installed_apps')", "Data"),
        Binding("5", "go('workspace_explorer')", "Explorer"),
        Binding("6", "go('installed_apps')", "AI"),
        Binding("7", "go('auth_module')", "Auth"),
        Binding("8", "go('installed_apps')", "Settings"),
        Binding("escape", "app.quit", "Exit"),
    ]

    DEFAULT_CSS = """
    HomeScreen #content-area {
        align: center middle;
    }

    #home-wrap {
        width: 66;
        height: auto;
        margin: 1 2;
    }

    #logo {
        width: 100%;
        height: auto;
        text-align: center;
        color: #89b4fa;
        text-style: bold;
    }

    #logo-sub {
        text-align: center;
        color: #585b70;
    }

    #device-panel {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        margin: 1 0;
        padding: 0 1;
    }

    #menu-panel {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 0 1;
    }

    #cmd-input {
        width: 100%;
        margin: 1 0 0 0;
        border: none;
        background: #1e1e2e;
        color: #cdd6f4;
        padding: 0 2;
    }

    #cmd-hint {
        color: #585b70;
        text-style: italic;
        padding: 0 2;
    }

    .home-label {
        color: #6c7086;
    }

    .menu-row {
        padding: 0 2;
    }
    """

    def body(self) -> ComposeResult:
        items = [
            ("1", "Monitor Runtime", "installed_apps"),
            ("2", "Analyze Installed Apps", "installed_apps"),
            ("3", "Collect APK", "installed_apps"),
            ("4", "Collect App Data (Root)", "installed_apps"),
            ("5", "Workspace Explorer", "workspace_explorer"),
            ("6", "AI Workspace", "installed_apps"),
            ("7", "Auth Module", "auth_module"),
            ("8", "Settings", "installed_apps"),
        ]
        with Vertical(id="home-wrap"):
            yield Static(LOGO, id="logo")
            yield Static("   [#585b70]Android Analysis Workspace  v1.0.0[/]", id="logo-sub")
            with Vertical(id="device-panel"):
                yield DevicePanel()
            with Vertical(id="menu-panel"):
                yield Static("  [#585b70]MENU[/]", classes="panel-title")
                yield Static("")
                for num, desc, target in items:
                    item = MenuItem(num, desc, action=target)
                    yield item
                yield Static("")
            yield Static(" [#585b70]type [bold]exit[/bold] or [bold]quit[/bold] to close[/]", id="cmd-hint")
            yield Input(placeholder="  enter command...", id="cmd-input")

    def on_mount(self):
        super().on_mount()
        self._timer = self.set_interval(5, self._check_device)
        self.run_worker(self._check_device(), exclusive=True)

    def on_unmount(self):
        timer = getattr(self, '_timer', None)
        if timer:
            timer.stop()

    async def _check_device(self):
        import logging
        import asyncio
        from textual.worker import WorkerCancelled
        logger = logging.getLogger("aaw")
        try:
            panel = self.query_one(DevicePanel)
            ok = await self.run_worker(is_adb_available, thread=True).wait()
            if not ok:
                panel.device_info = {"connected": False}
                return
            info = await self.run_worker(get_device_info, thread=True).wait()
            panel.device_info = info
        except (WorkerCancelled, asyncio.CancelledError):
            pass
        except Exception:
            logger.exception("_check_device failed")

    def action_go(self, screen: str):
        if screen == "quit":
            self.app.action_quit()
        else:
            self.app.navigate_to(screen)

    def on_menu_item_selected(self, event: MenuItem.Selected):
        action = event.item.action
        if action == "quit":
            self.app.action_quit()
        else:
            self.app.navigate_to(action)

    def on_input_submitted(self, event: Input.Submitted):
        cmd = event.value.strip().lower()
        inp = self.query_one("#cmd-input", Input)
        inp.clear()
        if cmd in ("exit", "quit", "q"):
            self.app.action_quit()
        elif cmd in ("help", "?"):
            self.notify_info(
                "Commands: [bold]exit[/], [bold]quit[/], [bold]q[/]  |  "
                "Menu items 1-8 can be clicked or pressed on keyboard  |  "
                "[bold]escape[/] to go back  |  [bold]F1[/] toggle sidebar",
                timeout=5,
            )
        elif cmd in ("1", "2", "3", "4", "5", "6", "7", "8"):
            targets = ["installed_apps", "installed_apps", "installed_apps",
                       "installed_apps", "workspace_explorer", "installed_apps",
                       "installed_apps", "installed_apps"]
            self.app.navigate_to(targets[int(cmd) - 1])
        elif cmd:
            self.notify_error(f"Unknown command: {cmd}. Type [bold]help[/] for commands.")
