from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Tree
from textual.binding import Binding
from textual.widgets.tree import TreeNode
from textual.app import ComposeResult

from aaw.screens.base import BaseScreen
from aaw.widgets import ActionItem

MODULE_DIR = "aaw/modules/auth"

MODULE_INFO = {
    "label": "Nusuk Auth Module",
    "package": "com.moh.nusukapp.auth.debug",
    "version": "1.0.0",
    "files": 29,
    "kotlin_files": 21,
    "resource_files": 6,
}


def _scan_tree(path: str) -> dict:
    import os
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
            with Vertical(id="actions-bar"):
                yield ActionItem("B", "Build APK (debug)", action="build_apk")
                yield ActionItem("I", "Install via ADB", action="install")
            with Vertical(id="module-footer"):
                yield Static(" [#f38ba8]B[/] Build  [#f38ba8]I[/] Install  [#f38ba8]ESC[/] Back")

    def action_build_apk(self):
        self.notify_info("[yellow]Building APK...[/] (mock)")

    def action_install(self):
        self.notify_info("[yellow]Installing via ADB...[/] (mock)")

    def on_action_item_selected(self, event: ActionItem.Selected):
        action = event.item.action
        if action == "build_apk":
            self.action_build_apk()
        elif action == "install":
            self.action_install()
