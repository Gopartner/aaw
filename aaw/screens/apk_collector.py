import os

from textual.containers import Vertical, Horizontal
from textual.widgets import Static
from textual.binding import Binding
from textual.app import ComposeResult

from aaw.utils import is_apktool_available, is_apksigner_available
from aaw.utils.apktool import pull_apk, repack_apk, sign_apk, BASE_OUTPUT
from aaw.screens.base import BaseScreen
from aaw.widgets import ActionItem


class APKCollectorScreen(BaseScreen):
    BINDINGS = [
        Binding("1", "pull", "Pull"),
        Binding("2", "unpack", "Unpack"),
        Binding("3", "repack", "Repack"),
        Binding("4", "sign", "Sign"),
        Binding("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    APKCollectorScreen #content-area {
        align: center top;
    }

    #apk-wrap {
        width: 78;
        height: auto;
        margin: 1 2;
    }

    #apk-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #app-info, #actions-panel, #status-panel, #tools-panel {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        margin: 1 0 0 0;
        padding: 0 1;
    }

    .al { color: #6c7086; }
    .av { color: #cdd6f4; }

    .action-row { padding: 0 1; }

    """

    def __init__(self, app_data: dict):
        super().__init__()
        self.app_data = app_data
        self._pulled_apk = None
        self._unpacked_dir = None
        self._repacked_apk = None

    def body(self) -> ComposeResult:
        a = self.app_data
        apktool_ok = is_apktool_available()
        apksigner_ok = is_apksigner_available()

        with Vertical(id="apk-wrap"):
            yield Static(" APK Tool ", id="apk-header")

            with Vertical(id="app-info"):
                yield Static("")
                yield Horizontal(Static("  App       ", classes="al"), Static(f" {a['name']}", classes="av"))
                yield Horizontal(Static("  Package   ", classes="al"), Static(f" {a['package']}", classes="av"))
                yield Static("")

            with Vertical(id="actions-panel"):
                yield Static("  [#585b70]ACTIONS[/]", classes="panel-title")
                yield Static("")
                for k, d, a in [("1", "Pull APK from device", "pull"), ("2", "Unpack APK", "unpack"),
                                ("3", "Repack APK", "repack"), ("4", "Sign APK", "sign")]:
                    yield ActionItem(k, d, action=a)
                yield Static("")

            with Vertical(id="status-panel"):
                yield Static("  [#585b70]STATUS[/]", classes="panel-title")
                yield Static("")
                for sid, label in [("s-pull", "Pull"), ("s-unpack", "Unpack"),
                                   ("s-repack", "Repack"), ("s-sign", "Sign")]:
                    yield Static(f"  [#6c7086]{label}:[/]  -", id=sid)
                yield Static("")

            with Vertical(id="tools-panel"):
                a1 = "[#a6e3a1]✔[/]" if apktool_ok else "[#f38ba8]✘[/]"
                a2 = "[#a6e3a1]✔[/]" if apksigner_ok else "[#f38ba8]✘[/]"
                yield Static(f"  [#6c7086]apktool[/]   {a1}")
                yield Static(f"  [#6c7086]apksigner[/] {a2}")

    def _set_status(self, sid: str, text: str):
        try:
            self.query_one(f"#{sid}", Static).update(f"  [#6c7086]{sid.split('-')[-1]}:[/] {text}")
        except Exception:
            pass

    def action_pull(self):
        a = self.app_data
        self._set_status("s-pull", "[#f9e2af]pulling...[/]")
        ok, msg = pull_apk(a["name"], a["package"])
        self._set_status("s-pull", f"[#a6e3a1]{msg}[/]" if ok else f"[#f38ba8]{msg}[/]")

    def action_unpack(self):
        if not is_apktool_available():
            self._set_status("s-unpack", "[#f38ba8]apktool not found[/]")
            return
        from aaw.utils.apktool import unpack_apk
        self._set_status("s-unpack", "[#f9e2af]unpacking...[/]")
        d = os.path.join(BASE_OUTPUT, "temp_unpacked")
        ok, msg = unpack_apk(d + ".apk", d)
        if ok:
            self._unpacked_dir = d
            self._set_status("s-unpack", f"[#a6e3a1]{msg}[/]")
        else:
            self._set_status("s-unpack", f"[#f38ba8]{msg}[/]")

    def action_repack(self):
        if not is_apktool_available():
            self._set_status("s-repack", "[#f38ba8]apktool not found[/]")
            return
        if not self._unpacked_dir:
            self._set_status("s-repack", "[#f9e2af]unpack first[/]")
            return
        self._set_status("s-repack", "[#f9e2af]repacking...[/]")
        ok, msg = repack_apk(self._unpacked_dir)
        if ok:
            self._repacked_apk = msg.split("(")[0].strip().replace("Repacked to ", "")
            self._set_status("s-repack", f"[#a6e3a1]{msg}[/]")
        else:
            self._set_status("s-repack", f"[#f38ba8]{msg}[/]")

    def action_sign(self):
        if not is_apksigner_available():
            self._set_status("s-sign", "[#f38ba8]apksigner not found[/]")
            return
        if not self._repacked_apk:
            self._set_status("s-sign", "[#f9e2af]repack first[/]")
            return
        self._set_status("s-sign", "[#f9e2af]signing...[/]")
        ok, msg = sign_apk(self._repacked_apk)
        self._set_status("s-sign", f"[#a6e3a1]{msg}[/]" if ok else f"[#f38ba8]{msg}[/]")

    def on_action_item_selected(self, event: ActionItem.Selected):
        action = event.item.action
        method = getattr(self, f"action_{action}", None)
        if method:
            method()
