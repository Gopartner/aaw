# AAW - Android Analysis Workspace

## Overview

AAW is a Textual-based TUI for Android app runtime analysis, with a modern responsive layout (sidebar on wide terminals), chat-like command input, and ADB integration.

## Tech Stack

- **Python >= 3.10**, **Textual >= 0.41.0**, **Rich >= 13.0.0**

## Project Structure

```
aaw/
├── __init__.py                # version: 1.0.0
├── __main__.py                # entry point (python -m aaw)
├── app.py                     # AAW App class + global CSS
├── data/
│   └── __init__.py            # mock data (10 apps, timeline, tree)
├── screens/
│   ├── __init__.py            # exports 10 classes (BaseScreen + 9 screens)
│   ├── base.py                # BaseScreen — responsive layout + sidebar
│   ├── home.py                # logo, device info, menu, command input
│   ├── installed_apps.py      # app list + search + filter
│   ├── app_dashboard.py       # app detail + actions
│   ├── auth_module.py         # auth module browser + build/install
│   ├── live_runtime.py        # activity monitor
│   ├── apk_collector.py       # APK pull/unpack/repack/sign
│   ├── root_data.py           # root data collection
│   ├── ai_workspace.py        # AI workspace generator
│   └── workspace_explorer.py  # file tree
└── utils/
│   ├── __init__.py            # re-exports all public functions
│   ├── adb.py                 # ADB device detection
│   ├── apktool.py             # apktool wrapper
│   └── log.py                 # file logger
└── widgets/
    ├── __init__.py            # exports Sidebar, SidebarItem, MenuItem, ActionItem
    ├── sidebar.py             # responsive sidebar nav + status
    └── menu.py                # MenuItem & ActionItem — clickable, hover, Selected message
```

## Color Scheme (Catppuccin Mocha)
- `#11111b` base bg, `#1e1e2e` surface, `#313244` overlay, `#45475a` border
- `#cdd6f4` text, `#585b70` subtext, `#6c7086` label
- `#89b4fa` blue/accent, `#a6e3a1` green, `#f38ba8` red, `#f9e2af` yellow

## Architecture

### BaseScreen Pattern
All screens extend `BaseScreen` (not `Screen` directly).

```python
class MyScreen(BaseScreen):
    def body(self) -> ComposeResult:
        yield Static("content")

    def on_mount(self):
        super().on_mount()
```

`BaseScreen` provides:
- Responsive layout: sidebar auto-hides below 110 columns (`@media`)
- `#content-area` (left, 1fr) + `#sidebar-container` (right, 22 cols)
- Header, Footer, sidebar with nav highlighting
- Helper methods: `notify_info()`, `notify_error()`, `notify_success()`

### Command Input (HomeScreen)
HomeScreen memiliki `Input` widget untuk command chat-like:
- `exit` / `quit` / `q` — quit application
- `help` / `?` — show available commands
- `1`–`8` — navigate to menu item

### Navigation
```python
# From any screen:
self.app.navigate_to("screen_key")
self.app.show_dashboard(app_data)   # push with data
self.app.show_live_runtime(data)
self.app.show_apk_collector(data)
self.app.show_root_data(data)
self.app.show_ai_workspace(data)
self.app.show_auth_module()
self.app.show_workspace_explorer()
```

### Sidebar
- `Sidebar.current_screen` reactive — auto-highlights nav item
- Shows ADB connection status
- Hidden on narrow terminals (check `self.app.size.width < 110` in `on_resize()`)

### Interactive Widgets (`aaw/widgets/menu.py`)
Clickable + hover items for menu and action lists.

- **`MenuItem(number, label, action)`** — Untuk menu navigasi. `number` ditampilkan sebagai key shortcut, `label` sebagai deskripsi, `action` sebagai target. Post `MenuItem.Selected` on click.
- **`ActionItem(key, label, action)`** — Untuk daftar aksi per-screen. `key` sebagai shortcut (1-8), `label` sebagai deskripsi, `action` sebagai nama method. Post `ActionItem.Selected` on click.

```python
# In compose/yield:
yield MenuItem("1", "Monitor Runtime", "installed_apps")

# In screen class, handle click:
def on_menu_item_selected(self, event: MenuItem.Selected):
    action = event.item.action
    self.app.navigate_to(action)
```

CSS: `hover { background: #313244; }`, cursor berubah menjadi hand saat hover.

### Exit / Terminal Safety
- `action_quit()` — tidak dioverride, pakai bawaan Textual (`self.exit()`)
- `on_exit()` — **TIDAK** override (jangan cancel semua asyncio task)
- `__main__._restore_console()` — safety net via Win32 `SetConsoleMode()` di `finally`
- Timer (`set_interval`) distop di `on_unmount()` untuk mencegah hang saat exit

### Adding a Screen
1. Create `aaw/screens/my_screen.py`, extend `BaseScreen`, implement `body()`
2. Register in `aaw/app.py` → `SCREENS` dict + optional nav method
3. Export in `aaw/screens/__init__.py`

### Code Style
- No unused imports
- Imports: stdlib → textual → aaw internal
- Every `__init__.py` has `__all__`
