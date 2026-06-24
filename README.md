# AAW - Android Analysis Workspace

> A modern Textual-based TUI (Terminal User Interface) for Android app runtime analysis.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Textual](https://img.shields.io/badge/Textual-8.2%2B-purple)

---

## Overview

AAW is an interactive terminal application for analyzing Android applications. It provides a keyboard-driven interface with mouse support for browsing installed apps, monitoring runtime behavior, collecting APK files, extracting data, and managing analysis workspaces.

Built with [Textual](https://textual.textualize.io/) — the modern TUI framework for Python.

## Features

- **Device Detection** — Real ADB device detection with connection status and root access info
- **App Browser** — List installed apps with search, filtering (User / System / Vendor), and size display
- **App Actions** — Analyze, unpack APK, uninstall, backup data, reset app
- **Runtime Monitor** — Live activity timeline and stats
- **APK Toolkit** — Pull APKs from device, unpack with apktool, repack, and sign
- **Root Data Collection** — Collect app data directories (databases, shared prefs, files, cache)
- **AI Workspace Generator** — Generate analysis workspaces with README, summaries, and prompt files
- **Workspace Explorer** — Browse generated workspaces in a file tree
- **Responsive Sidebar** — Auto-hides on narrow terminals (<110 columns), togglable with F1
- **Modern UI** — Catppuccin Mocha color scheme, hover animations, click interactions
- **Command Input** — Chat-like command prompt for exit, help, and navigation

## Requirements

- Python **3.10+**
- [Textual](https://pypi.org/project/textual/) **>= 8.2.0**
- [Rich](https://pypi.org/project/rich/) **>= 13.0.0**
- (Optional) `adb` in PATH for real device detection
- (Optional) `apktool` + `apksigner` in PATH for APK unpacking/repacking

## Installation

```bash
# Clone the repository
git clone https://github.com/gopartner/aaw.git
cd aaw

# Install dependencies
pip install textual rich

# Run
python -m aaw
```

Or install as a package:

```bash
pip install -e .
python -m aaw
```

## Usage

### Command Input (Home Screen)

Type commands directly into the input field at the bottom of the home screen:

| Command       | Action                     |
|---------------|----------------------------|
| `exit`, `quit`, `q` | Quit the application |
| `help`, `?`   | Show available commands    |
| `1` - `8`     | Navigate to menu item      |

### Menu Navigation

Press **1**-**8** or click any menu item to navigate:

| Key | Feature                |
|-----|------------------------|
| 1   | Monitor Runtime        |
| 2   | Analyze Installed Apps |
| 3   | Collect APK            |
| 4   | Collect App Data (Root)|
| 5   | Workspace Explorer     |
| 6   | AI Workspace           |
| 7   | Reports                |
| 8   | Settings               |

### Global Keys

| Key       | Action                     |
|-----------|----------------------------|
| `q`       | Quit application           |
| `Escape`  | Go back / Quit on home     |
| `F1`      | Toggle sidebar             |
| `Enter`   | Select / Analyze           |
| `↑` `↓`  | Navigate list              |

### App List (Installed Apps)

- **Filter**: Click **All** / **User** / **System** / **Vendor** buttons
- **Search**: Type in the search box
- **Select**: Click any app to show action panel on the right
- **Actions**: Analyze, Unpack APK, Uninstall, Backup Data, Backup APK+Data, Reset

## Project Structure

```
aaw/
├── aaw/
│   ├── __init__.py            # Version info
│   ├── __main__.py            # Entry point (python -m aaw)
│   ├── app.py                 # Main App class + global CSS
│   ├── data/
│   │   └── __init__.py        # Mock data (apps, timeline, etc.)
│   ├── screens/
│   │   ├── base.py            # BaseScreen — responsive layout + sidebar
│   │   ├── home.py            # Home screen — logo, device panel, command input
│   │   ├── installed_apps.py  # App list with filters + action panel
│   │   ├── app_dashboard.py   # App detail + actions
│   │   ├── live_runtime.py    # Activity timeline monitor
│   │   ├── apk_collector.py   # APK pull/unpack/repack/sign
│   │   ├── root_data.py       # Root data collection
│   │   ├── ai_workspace.py    # AI workspace generator
│   │   └── workspace_explorer.py  # File tree browser
│   ├── utils/
│   │   ├── adb.py             # ADB device detection
│   │   ├── apktool.py         # APK tool wrapper
│   │   └── log.py             # File logger
│   └── widgets/
│       ├── sidebar.py         # Responsive sidebar nav + ADB status
│       └── menu.py            # Clickable MenuItem & ActionItem widgets
├── AGENTS.md                  # AI agent documentation
├── pyproject.toml             # Project config
└── README.md
```

## Development

### Adding a New Screen

1. Create `aaw/screens/my_screen.py` extending `BaseScreen`
2. Implement `body()` method returning `ComposeResult`
3. Register in `aaw/app.py` → add to `SCREENS` dict
4. Export in `aaw/screens/__init__.py`

### Code Style

- Follow existing patterns and conventions
- No unused imports
- Import order: stdlib → textual → aaw internal
- Every `__init__.py` has `__all__`

### Testing

```bash
python -m aaw
```

## Color Scheme

Catppuccin Mocha palette:

| Token      | Hex       | Usage            |
|------------|-----------|------------------|
| Base       | `#11111b` | Background       |
| Surface    | `#1e1e2e` | Panel background |
| Overlay    | `#313244` | Hover / border   |
| Text       | `#cdd6f4` | Primary text     |
| Subtext    | `#585b70` | Secondary text   |
| Blue       | `#89b4fa` | Accent / links   |
| Green      | `#a6e3a1` | Success          |
| Red        | `#f38ba8` | Error / danger   |
| Yellow     | `#f9e2af` | Warning          |

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built with [Textual](https://github.com/Textualize/textual)*
