from textual.containers import Vertical, Horizontal
from textual.widgets import Static, Input, ListView, ListItem, Button
from textual.binding import Binding
from textual.app import ComposeResult
from textual.reactive import reactive

from aaw.data import MOCK_APPS
from aaw.screens.base import BaseScreen
from aaw.widgets import ActionItem


FILTERS = [
    ("All", "all", "#a6e3a1"),
    ("User", "user", "#89b4fa"),
    ("System", "system", "#f9e2af"),
    ("Vendor", "vendor", "#f38ba8"),
]

ACTIONS = [
    ("1", "Analyze", "analyze"),
    ("2", "Unpack (copy APK)", "unpack"),
    ("3", "Uninstall", "uninstall"),
    ("4", "Backup Data Only", "backup_data"),
    ("5", "Backup APK + Data", "backup_full"),
    ("6", "Reset App", "reset"),
]


class AppListItem(ListItem):
    def __init__(self, app_data: dict, **kwargs):
        super().__init__(**kwargs)
        self.app_data = app_data

    def compose(self):
        a = self.app_data
        sz = f"{a['size']:.1f} MB" if a['size'] < 1024 else f"{a['size']/1024:.1f} GB"
        yield Static(f"  [bold #cdd6f4]{a['name']}[/]  [#585b70]{sz}[/]", classes="app-top")
        yield Static(f"  [#6c7086]{a['package']}[/]", classes="app-pkg")


class InstalledAppsScreen(BaseScreen):
    filter = reactive("all", init=False)
    selected_app = reactive(None, init=False)

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("enter", "select_app", "Analyze"),
    ]

    DEFAULT_CSS = """
    InstalledAppsScreen #content-area {
        align: center top;
    }

    #left-panel {
        width: 1fr;
        height: 100%;
        min-width: 50;
        margin: 1 0 1 2;
    }

    #action-panel {
        width: 34;
        height: 100%;
        margin: 1 2 1 0;
        border: round #45475a;
        background: #1e1e2e;
        display: none;
        overflow-y: auto;
    }

    #action-panel.show {
        display: block;
    }

    #action-header {
        border-bottom: solid #313244;
        padding: 1 2;
        height: auto;
    }

    #action-header-name {
        text-style: bold;
        color: #cdd6f4;
    }

    #action-header-pkg {
        color: #585b70;
    }

    #action-header-size {
        color: #6c7086;
    }

    #action-list {
        padding: 1 0;
    }

    #action-list ActionItem {
        height: 3;
        padding: 0 1;
    }

    #action-list ActionItem:hover {
        background: #313244;
    }

    #apps-header {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 0 1;
        text-align: center;
        text-style: bold;
        color: #89b4fa;
    }

    #filter-bar {
        margin: 1 0;
        height: auto;
    }

    #filter-bar Button {
        min-width: 10;
        margin: 0 0 0 0;
    }

    .filter-btn {
        background: #313244;
        color: #cdd6f4;
        border: none;
        padding: 0 1;
    }

    .filter-btn:hover {
        background: #45475a;
    }

    .filter-btn.active {
        background: #45475a;
        color: #89b4fa;
        text-style: bold;
    }

    #search-box {
        margin: 0 0 1 0;
    }

    #app-count {
        color: #585b70;
        margin: 0 0 1 0;
    }

    #app-list {
        width: 100%;
        height: 1fr;
        border: round #313244;
        background: #1e1e2e;
    }

    AppListItem {
        height: 3;
        padding: 0 1;
        border-bottom: solid #313244;
    }

    AppListItem:hover {
        background: #313244;
    }

    .app-top {
        padding: 1 0 0 0;
    }

    .app-pkg {
        padding: 0 0 1 0;
    }

    #apps-footer {
        border: round #313244;
        background: #1e1e2e;
        width: 100%;
        height: auto;
        padding: 0 1;
        margin: 1 0 0 0;
    }

    .footer-text {
        color: #585b70;
    }
    """

    def _filtered_apps(self):
        q = self._query if hasattr(self, '_query') else ""
        apps = MOCK_APPS
        if self.filter != "all":
            apps = [a for a in apps if a.get("type_key") == self.filter]
        if q:
            apps = [a for a in apps if q in a["name"].lower() or q in a["package"].lower()]
        return apps

    def _rebuild_list(self):
        lv = self.query_one("#app-list", ListView)
        lv.clear()
        apps = self._filtered_apps()
        if not apps:
            lv.mount(ListItem(Static(" [#585b70]no matches[/]")))
        else:
            for a in apps:
                lv.mount(AppListItem(a))
        self.query_one("#app-count", Static).update(f" [#585b70]{len(apps)} apps[/]")
        sa = self.selected_app
        if sa is not None and sa not in apps:
            self.selected_app = None

    def _update_action_panel(self):
        panel = self.query_one("#action-panel")
        app = self.selected_app
        if app is None:
            panel.remove_class("show")
            return
        panel.add_class("show")
        self.query_one("#action-header-name", Static).update(f"  [bold #cdd6f4]{app['name']}[/]")
        self.query_one("#action-header-pkg", Static).update(f"  [#585b70]{app['package']}[/]")
        sz = f"{app['size']:.1f} MB" if app['size'] < 1024 else f"{app['size']/1024:.1f} GB"
        self.query_one("#action-header-size", Static).update(f"  [#6c7086]{sz}[/]  [{_type_color(app['type'])}]{app['type']}[/]")
        al = self.query_one("#action-list")
        al.remove_children()
        for k, desc, a in ACTIONS:
            al.mount(ActionItem(k, desc, action=a))

    def _on_action(self, action: str):
        app = self.selected_app
        if app is None:
            return
        msgs = {
            "analyze": f"Analyzing {app['name']}...",
            "unpack": f"Unpacking {app['package']}.apk to laptop...",
            "uninstall": f"Uninstalling {app['name']}...",
            "backup_data": f"Backing up data for {app['name']}...",
            "backup_full": f"Backing up APK + data for {app['name']}...",
            "reset": f"Resetting {app['name']}...",
        }
        msg = msgs.get(action, f"Action '{action}' for {app['name']}")
        if action == "analyze":
            self.app.show_dashboard(app)
        elif action == "uninstall":
            self.notify_info(f"[red]Uninstalling[/] {app['name']}... (mock)")
            MOCK_APPS.remove(app)
            self.selected_app = None
            self._rebuild_list()
        else:
            self.notify_info(msg)

    def body(self) -> ComposeResult:
        with Horizontal():
            with Vertical(id="left-panel"):
                yield Static(" Installed Applications ", id="apps-header")
                with Horizontal(id="filter-bar"):
                    for label, key, color in FILTERS:
                        btn = Button(label, classes="filter-btn", id=f"filter-{key}")
                        yield btn
                yield Input(placeholder="Search . . .", id="search-box")
                yield Static(f" [#585b70]{len(MOCK_APPS)} apps[/]", id="app-count")
                with ListView(id="app-list"):
                    for a in MOCK_APPS:
                        yield AppListItem(a)
                with Vertical(id="apps-footer"):
                    yield Static(" [#f38ba8]ENTER[/] Analyze  [#f38ba8]CLICK[/] Select  [#f38ba8]ESC[/] Back", classes="footer-text")
            with Vertical(id="action-panel"):
                with Vertical(id="action-header"):
                    yield Static("", id="action-header-name")
                    yield Static("", id="action-header-pkg")
                    yield Static("", id="action-header-size")
                with Vertical(id="action-list"):
                    pass

    def on_mount(self):
        super().on_mount()
        self._query = ""

    def watch_filter(self, new_filter: str):
        for label, key, color in FILTERS:
            btn = self.query_one(f"#filter-{key}", Button)
            btn.classes = "filter-btn active" if key == new_filter else "filter-btn"
        self._rebuild_list()

    def watch_selected_app(self, app):
        self._update_action_panel()

    def on_button_pressed(self, event: Button.Pressed):
        btn_id = event.button.id or ""
        if btn_id.startswith("filter-"):
            self.filter = btn_id.removeprefix("filter-")

    def on_input_changed(self, event: Input.Changed):
        self._query = event.value.lower()
        self._rebuild_list()

    def on_list_view_selected(self, event: ListView.Selected):
        item = event.item
        if hasattr(item, "app_data"):
            self.selected_app = item.app_data

    def action_select_app(self):
        lv = self.query_one("#app-list", ListView)
        c = lv.highlighted_child
        if c and hasattr(c, "app_data"):
            self.app.show_dashboard(c.app_data)

    def on_action_item_selected(self, event: ActionItem.Selected):
        self._on_action(event.item.action)


def _type_color(t: str) -> str:
    return {"User App": "#a6e3a1", "System App": "#89b4fa", "Vendor": "#f9e2af"}.get(t, "#cdd6f4")
