# Gonky

A GUI application for generating custom [Conky](https://github.com/brndnmtthws/conky)
configuration files. Drag and drop system-monitoring components onto a canvas, configure
their properties, and export a ready-to-use `~/.config/conky/conky.conf`.

## Features

- **Visual canvas editor** — drag components from the library and position them freely;
  vertical order on the canvas maps directly to the order of blocks in the generated config.
- **Component library** — 20+ built-in component types covering CPU, memory, disk, network,
  battery, temperature, clock, graphs, bars, separators, custom text, and Lua snippets.
- **Live properties panel** — click any canvas tile to edit its label, color, font, and all
  type-specific settings through auto-generated form fields with tooltips.
- **Global settings dialog** — configure window geometry, alignment, background, update
  interval, and default font for the Conky window.
- **Live preview** — toggle a real Conky subprocess that renders the generated config on the
  desktop and auto-refreshes within ~1.5 s of any property change.
- **Save / Load** — persist work as a `.gonky` JSON project file and reload it later.
- **Export** — write a clean `conky.conf` to any path (default: `~/.config/conky/conky.conf`).
- **Keyboard shortcuts** — Ctrl+N (New), Ctrl+O (Open), Ctrl+S (Save), Ctrl+E (Export),
  Ctrl+P (Preview), Ctrl+Q (Quit), Delete (remove selected canvas tile).
- **Validation** — pre-export checks warn about empty canvases, duplicate Y-positions, and
  disabled-only canvases; errors block export while warnings allow the user to proceed.

## System Requirements

- **Python 3.10+**
- **GTK 4** (4.6 or newer recommended; 4.10+ for best file-dialog support)
  — provided by the `python3-gi` system package **or** via pip (see below)
- **Conky 1.12+** — required only for the live preview feature; the editor itself works
  without Conky installed

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/gonky.git
cd gonky
```

### 2. Install system dependencies

Gonky uses GTK 4 via PyGObject. The recommended way is to install the system package:

**Ubuntu / Debian:**
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0
```

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4
```

**Arch Linux:**
```bash
sudo pacman -S python-gobject gtk4
```

**Fallback (pip):**
If the system package is not available or you prefer a virtualenv-only setup:
```bash
pip install PyGObject
```
Note: `pip install PyGObject` requires the GTK 4 development headers and `pkg-config`
to be present on the system (`sudo apt install libgtk-4-dev` on Debian/Ubuntu).

### 3. Create a virtual environment and install Gonky

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

> **Note:** If you installed `python3-gi` as a system package, create the virtual
> environment with `--system-site-packages` so PyGObject is accessible inside it:
>
> ```bash
> python3 -m venv --system-site-packages .venv
> source .venv/bin/activate
> pip install -e .
> ```

### 4. (Optional) Install development dependencies

```bash
pip install -r requirements-dev.txt
```

## Running the App

```bash
python -m gonky
```

Or, after `pip install -e .`:

```bash
gonky
```

## Running Tests

```bash
pytest
```

With coverage:

```bash
pytest --cov=src/gonky --cov-report=term-missing
```

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+N | New project |
| Ctrl+O | Open project |
| Ctrl+S | Save project |
| Ctrl+E | Export Conky config |
| Ctrl+P | Toggle live preview |
| Ctrl+Q | Quit |
| Delete | Remove selected canvas tile |

## Known Limitations

- **Y-sort → linear output:** Components are sorted by their vertical position on the canvas
  when the config is generated. Two tiles at the same Y coordinate have an unspecified
  relative order in the output. Place tiles at different heights to control their order.
- **No undo/redo:** All canvas and property changes are immediate and cannot be reversed
  within a session. Save frequently.
- **No import of existing configs:** Gonky cannot parse an existing `conky.conf` and
  reconstruct a GUI state from it. You must build configs from scratch.
- **Preview conflicts:** The live preview starts a new Conky process with `--config`. If
  another Conky instance is already running without `--config`, both may be active at the
  same time. Stop any existing Conky instance before toggling the preview.
- **Minimum Conky version:** The generated config syntax targets Conky 1.12+. Older
  versions may not support all used variables or config keys.

## Project Structure

```
gonky/
├── pyproject.toml          # Build metadata and entry point
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies
├── docs/                   # Technical documentation and roadmap
├── assets/                 # Icons and CSS stylesheet
├── src/gonky/              # Application source
│   ├── app.py              # Gtk.Application subclass + keyboard shortcuts
│   ├── constants.py        # App-wide constants and paths
│   ├── models/             # Pure Python data layer (no GTK)
│   ├── logic/              # Business logic: config gen, file I/O, preview
│   ├── ui/                 # GTK 4 widgets and windows
│   └── components/         # Conky component definitions and registry
└── tests/                  # pytest test suite
```

See [`docs/tech-stack.md`](docs/tech-stack.md) for the full technology choice rationale and
[`docs/post-v1-roadmap.md`](docs/post-v1-roadmap.md) for planned future features.

## License

See [LICENSE](LICENSE).
