from textual.widgets import Static
from textual.message import Message


class MenuItem(Static):
    class Selected(Message):
        def __init__(self, item: "MenuItem") -> None:
            super().__init__()
            self.item = item

    def __init__(
        self,
        number: str,
        label: str,
        action: str = "",
        shortcut: str = "",
    ) -> None:
        super().__init__()
        self.number = number
        self.label = label
        self.action = action
        self.shortcut = shortcut

    def render(self) -> str:
        prefix = f"[bold #89b4fa]{self.number}[/]  " if self.number else ""
        lbl = f"[#cdd6f4]{self.label}[/]" if self.label else ""
        sc = f"  [#585b70]{self.shortcut}[/]" if self.shortcut else ""
        return f"  {prefix}{lbl}{sc}"

    DEFAULT_CSS = """
    MenuItem {
        padding: 0 2;
        height: 2;
    }
    MenuItem:hover {
        background: #313244;
        color: #89b4fa;
    }
    MenuItem:focus {
        background: #45475a;
    }
    """

    def on_click(self):
        if self.action:
            self.post_message(self.Selected(self))


class ActionItem(Static):
    class Selected(Message):
        def __init__(self, item: "ActionItem") -> None:
            super().__init__()
            self.item = item

    def __init__(self, key: str, label: str, action: str = "") -> None:
        super().__init__()
        self.key = key
        self.label = label
        self.action = action

    def render(self) -> str:
        return f"  [#89b4fa]{self.key}[/]  [#cdd6f4]{self.label}[/]"

    DEFAULT_CSS = """
    ActionItem {
        padding: 0 2;
        height: 2;
    }
    ActionItem:hover {
        background: #313244;
        color: #f38ba8;
    }
    ActionItem:focus {
        background: #45475a;
    }
    """

    def on_click(self):
        if self.action:
            self.post_message(self.Selected(self))
