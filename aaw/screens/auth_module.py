import os
import subprocess
import logging
import asyncio

from textual.containers import Vertical
from textual.widgets import Static, Tree
from textual.binding import Binding
from textual.widgets.tree import TreeNode
from textual.app import ComposeResult
from textual.worker import WorkerCancelled

from aaw.screens.base import BaseScreen
from aaw.utils import is_adb_available, is_apk_built, install_apk
from aaw.widgets import ActionItem

logger = logging.getLogger("aaw.auth_module")

MODULE_DIR = "aaw/modules/auth"

MODULE_INFO = {
    "label": "Nusuk Auth Module",
    "package": "com.moh.nusukapp.auth.debug",
    "version": "1.0.0",
    "files": 30,
    "kotlin_files": 22,
    "resource_files": 6,
}

APK_OUTPUT = os.path.join(MODULE_DIR, "build", "apk", "NusukAuthDebug.apk")


def _scan_tree(path: str) -> dict:
    result = {}
    try:
        for entry in os.listdir(path):
            entry_path = os.path.join(path, entry)
            if os.path.isdir(entry_path):
                children = _scan_tree(entry_path)
                if children:
                    result[entry] = children
                else:
                    result[entry] = {}
            else:
                result[entry] = None
    except PermissionError:
        pass
    return result


def build_tree(parent: TreeNode, data: dict):
    for name, children in sorted(data.items()):
        if children is not None:
            node = parent.add(f"[#89b4fa]{name}[/]", expand=False)
            build_tree(node, children)
        else:
            parent.add_leaf(f"[#585b70]{name}[/]")


class AuthModuleScreen(BaseScreen):
    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("b", "build_apk", "Build"),
        Binding("i", "install", "Install"),
    ]

    DEFAULT_CSS = """
    AuthModuleScreen #content-area {
        align: center top;
    }

    #module-wrap {
        width: 74;
        height: 100%;
        margin: 1 2;
    }

    #module-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #module-info {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 1 2;
        margin: 1 0;
    }

    .info-row {
        padding: 0 1;
    }

    #file-tree {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: 1fr;
        margin: 0 0 1 0;
        padding: 0 1;
    }

    Tree {
        background: #1e1e2e;
        color: #cdd6f4;
    }

    Tree:focus {
        border: none;
    }

    #status-panel {
        border: round #45475a;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        padding: 0 1;
    }

    #log-panel {
        border: round #45475a;
        background: #11111b;
        width: 100%;
        height: 8;
        margin: 0 0 1 0;
        padding: 0 1;
        overflow-y: auto;
        visibility: hidden;
    }

    #actions-bar {
        border: round #45475a;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        margin: 0 0 1 0;
        padding: 0 1;
    }

    #actions-bar ActionItem {
        height: 3;
        padding: 0 1;
    }

    #actions-bar ActionItem:hover {
        background: #313244;
    }

    #module-footer {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        padding: 0 1;
    }
    """

    def __init__(self):
        super().__init__()
        self._building = False
        self._build_progress = 0
        self._build_timer = None
        self._build_output_lines = []

    def body(self) -> ComposeResult:
        info = MODULE_INFO
        with Vertical(id="module-wrap"):
            yield Static(f" {info['label']} ", id="module-header")
            with Vertical(id="module-info"):
                yield Static(f"  [#6c7086]Package[/]     [#cdd6f4]{info['package']}", classes="info-row")
                yield Static(f"  [#6c7086]Version[/]     [#cdd6f4]{info['version']}", classes="info-row")
                yield Static(f"  [#6c7086]Source[/]     [#cdd6f4]aaw/modules/auth/", classes="info-row")
                yield Static(f"  [#6c7086]Files[/]      [#cdd6f4]{info['files']} total  ({info['kotlin_files']} Kotlin, {info['resource_files']} resources)", classes="info-row")
            tree = Tree("modules/auth/", id="file-tree")
            tree.root.expand()
            tree_data = _scan_tree(MODULE_DIR)
            build_tree(tree.root, tree_data)
            yield tree
            with Vertical(id="status-panel"):
                yield Static("  [#585b70]STATUS[/]", classes="panel-title")
                yield Static("")
                yield Static("  [#6c7086]Build:[/]   -", id="s-build")
                yield Static("  [#6c7086]Install:[/] -", id="s-install")
                yield Static("")
            with Vertical(id="log-panel"):
                yield Static("  [#585b70]BUILD LOG[/]", id="log-header")
                yield Static("", id="log-content")
            with Vertical(id="actions-bar"):
                yield ActionItem("B", "Build APK (debug)", action="build_apk")
                yield ActionItem("I", "Install via ADB", action="install")
            with Vertical(id="module-footer"):
                yield Static(" [#f38ba8]B[/] Build  [#f38ba8]I[/] Install  [#f38ba8]ESC[/] Back")

    def _set_status(self, sid: str, text: str):
        try:
            label = sid.split("-")[-1]
            self.query_one(f"#{sid}", Static).update(f"  [#6c7086]{label}:[/] {text}")
        except Exception:
            pass

    def _append_log(self, line: str):
        self._build_output_lines.append(line)
        max_lines = 15
        visible = self._build_output_lines[-max_lines:]
        try:
            panel = self.query_one("#log-panel", Vertical)
            panel.styles.visibility = "visible"
            content = self.query_one("#log-content", Static)
            content.update("\n".join(visible))
        except Exception:
            pass

    def _animate_build(self):
        if not self._building:
            return
        self._build_progress += 1
        dots = "." * ((self._build_progress % 3) + 1)
        self._set_status("s-build", f"[#f9e2af]building{dots}[/]")

    def _run_build_script(self) -> tuple[bool, str]:
        script_path = os.path.join(MODULE_DIR, "build_debug.ps1")
        if not os.path.isfile(script_path):
            return False, "Build script not found: build_debug.ps1"
        try:
            result = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path],
                capture_output=True, text=True, timeout=300,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            out = (result.stdout or "").strip()
            err = (result.stderr or "").strip()
            for line in out.splitlines():
                self._append_log(line)
            if err:
                self._append_log(f"[red]{err}[/]")
            if result.returncode == 0:
                return True, "Build succeeded"
            else:
                msg = err or out or f"Exit code {result.returncode}"
                return False, msg
        except subprocess.TimeoutExpired:
            self._append_log("[red]Build timed out (300s)[/]")
            return False, "Build timed out (300s)"
        except FileNotFoundError:
            self._append_log("[red]powershell not found[/]")
            return False, "powershell not found"
        except Exception as e:
            self._append_log(f"[red]{e}[/]")
            return False, str(e)

    async def action_build_apk(self):
        if self._building:
            self.notify_warning("Build already in progress")
            return
        self._building = True
        self._build_progress = 0
        self._build_output_lines = []
        self._set_status("s-build", "[#f9e2af]starting...[/]")
        self._build_timer = self.set_interval(0.5, self._animate_build)
        try:
            ok, msg = await self.run_worker(self._run_build_script, thread=True).wait()
            self._set_status("s-build", f"[#a6e3a1]{msg}[/]" if ok else f"[#f38ba8]{msg}[/]")
            if ok:
                self.notify_success("[green]Build OK[/]")
            else:
                self.notify_error(f"[red]Build failed: {msg}[/]")
        except WorkerCancelled:
            self._set_status("s-build", "[#f38ba8]cancelled[/]")
        finally:
            self._building = False
            if self._build_timer:
                self._build_timer.stop()
                self._build_timer = None

    async def action_install(self):
        if not is_adb_available():
            self._set_status("s-install", "[#f38ba8]adb not found[/]")
            self.notify_error("[red]ADB not available[/]")
            return
        if not is_apk_built(APK_OUTPUT):
            self._set_status("s-install", "[#f9e2af]APK not found, build first[/]")
            self.notify_warning("[yellow]Build the APK first[/]")
            return
        self._set_status("s-install", "[#f9e2af]installing...[/]")
        self.notify_info("[yellow]Installing via ADB...[/]")
        ok, msg = await self.run_worker(install_apk, thread=True, args=(APK_OUTPUT,)).wait()
        self._set_status("s-install", f"[#a6e3a1]{msg}[/]" if ok else f"[#f38ba8]{msg}[/]")
        if ok:
            self.notify_success("[green]Install OK[/]")
        else:
            self.notify_error(f"[red]Install failed: {msg}[/]")

    def on_action_item_selected(self, event: ActionItem.Selected):
        action = event.item.action
        if action == "build_apk":
            self.run_worker(self.action_build_apk(), exclusive=True)
        elif action == "install":
            self.run_worker(self.action_install(), exclusive=True)
