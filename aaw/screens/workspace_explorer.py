from textual.containers import Vertical
from textual.widgets import Static, Tree
from textual.binding import Binding
from textual.widgets.tree import TreeNode
from textual.app import ComposeResult

from aaw.screens.base import BaseScreen

TREE_DATA = {
    "output": {
        "WhatsApp": {
            "com.whatsapp": {
                "09-15-22_kamis-25-06-2026": {},
                "10-15-22_kamis-25-06-2026": {
                    "README.md": None,
                    "SUMMARY.md": None,
                    "AI_CONTEXT.md": None,
                    "runtime": {},
                    "app": {},
                    "data": {},
                    "reports": {},
                    "graphs": {},
                    "prompts": {},
                },
                "latest": {},
            },
        },
    },
}


def build_tree(parent: TreeNode, data: dict):
    for name, children in data.items():
        if children is not None and len(children) > 0:
            node = parent.add(name, expand=True)
            build_tree(node, children)
        else:
            parent.add_leaf(name)


class WorkspaceExplorerScreen(BaseScreen):
    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("escape", "go_back", "Back"),
    ]

    DEFAULT_CSS = """
    WorkspaceExplorerScreen #content-area {
        align: center top;
    }

    #explorer-wrap {
        width: 74;
        height: 100%;
        margin: 1 2;
    }

    #explorer-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #file-tree {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: 1fr;
        margin: 1 0;
        padding: 0 1;
    }

    Tree {
        background: #1e1e2e;
        color: #cdd6f4;
    }

    Tree:focus {
        border: none;
    }

    #explorer-footer {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        padding: 0 1;
    }

    """

    def body(self) -> ComposeResult:
        with Vertical(id="explorer-wrap"):
            yield Static(" Workspace Explorer ", id="explorer-header")

            tree = Tree("output/", id="file-tree")
            tree.root.expand()
            build_tree(tree.root, TREE_DATA)
            yield tree

            with Vertical(id="explorer-footer"):
                yield Static(" [#f38ba8]ESC[/] Back  [#f38ba8]R[/] Refresh  [#f38ba8]Q[/] Quit")

    def action_refresh(self):
        pass
