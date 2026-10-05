# Technology Stack Rationale — Gonky

## Overview

Gonky is a GUI front-end for generating Conky configuration files. This document records the
reasoning behind every significant technology choice for v1.

---

## Language: Python 3.10+

**Gonky does not interact with Conky's source code.** Although Conky itself is written in C++,
Gonky's only integration surface with Conky is a plain-text `.conf` file and a shell process
(`conky -c <path>`). There is no `libconky` API to bind against and no shared data structures
to exchange. The language choice is therefore purely a GUI development productivity decision.

### Why not C++?

| Concern | Python 3 | C++ |
|---|---|---|
| Integration with Conky | Text file + subprocess — identical in both languages | Text file + subprocess — identical in both languages |
| GUI framework binding quality | PyGObject (GTK 4) is idiomatic Python, well-maintained, widely documented | gtkmm (GTK 4 C++ binding) is excellent but ~3× more verbose per widget |
| Development speed | Dataclasses, stdlib JSON, `subprocess`, `pathlib` — zero extra dependencies for core logic | Manual memory management, no stdlib JSON, heavier build system (CMake/Meson) |
| Drag-and-drop canvas | `Gtk.DragSource` / `Gtk.DropTarget` in ~15 lines | Same API in gtkmm — equivalent complexity, significantly more boilerplate |
| Config generation | f-strings, string formatting — trivial | Doable but no advantage; more ceremony |
| Cross-distro packaging | `python3-gi` ships on Ubuntu, Fedora, Arch, Debian — or `pip install PyGObject` | Requires a compiled binary per distribution/architecture |
| Testability | `pytest` + zero-dependency unit tests for pure functions | GTest/Catch2 work fine but add CMake complexity |
| Runtime performance | Not a bottleneck — the app generates text and manages a subprocess | Not a bottleneck |

**When C++ would be the right choice:** if Gonky needed to link against a native Conky library,
perform real-time system-level rendering, or ship as a size-constrained system utility with no
interpreter. None of these apply.

### Why not Rust (gtk-rs)?

Rust + GTK 4 via `gtk-rs` is a modern, high-quality option. Rejected for v1 because the learning
curve for Rust ownership semantics combined with GTK 4's callback-heavy API is a significant
productivity tax on a first-version GUI application. Post-v1 rewrite is viable.

### Why not Qt (PyQt6 / PySide6)?

PyQt6 carries GPL/commercial licensing nuance. PySide6 (LGPL) is fine but adds a heavier
dependency that is not pre-installed on most Linux desktops. GTK 4 is the native Linux toolkit
and is already present on GNOME-based distributions.

### Why not Electron/Tauri?

Electron adds ~200 MB of Node.js/Chromium overhead. Tauri (Rust + WebView) is lighter but
inherits the Rust complexity concern above. Neither produces a native Linux look-and-feel.

**Verdict: Python 3.10+ with GTK 4 via PyGObject.**

---

## GUI Framework: GTK 4 via PyGObject

- **PyGObject** — Python bindings for GLib/GObject/GTK 4. Install via `pip install PyGObject`
  or distro package `python3-gi`. Minimum version: PyGObject 3.42 (GTK 4.6+).
- **`Gtk.Application`** — application lifecycle, single-instance enforcement, action registration.
- **`Gtk.ApplicationWindow`** — main window.
- **`Gtk.Fixed`** — free-position canvas container for drag-and-drop component placement.
- **`Gtk.DragSource` / `Gtk.DropTarget`** — GTK 4 drag-and-drop API (replaces the deprecated
  GTK 3 `drag_source_set` / `drag_dest_set`).
- **`Gtk.ListBox`** — component library panel.
- **`Gtk.SpinButton`, `Gtk.Entry`, `Gtk.Switch`, `Gtk.ColorButton`, `Gtk.DropDown`,
  `Gtk.FontButton`** — property form widgets.
- **`Gtk.Paned`** — resizable panel splitter.
- **`Gtk.CssProvider`** — load `assets/styles/gonky.css` for visual theming.
- **`Gtk.FileDialog`** — GTK 4 async file chooser (replaces `Gtk.FileChooserDialog`).
- **`Gtk.MessageDialog`** — error and confirmation dialogs.
- **`GLib.timeout_add`** — debounce timer for preview refresh.

---

## Core Python Standard Library Modules

| Module | Usage |
|---|---|
| `dataclasses` | `GlobalConkySettings`, `ConkyComponent`, `GonkyDocument`, `PropertyField`, `ValidationError` |
| `json` | Project file serialisation/deserialisation |
| `pathlib.Path` | All file path handling — cross-distro, no string concatenation |
| `subprocess` | Launch, monitor, and terminate the Conky preview process |
| `shutil` | `shutil.which("conky")` — detect if Conky is installed |
| `uuid` | Generate unique `id` for each `ConkyComponent` |
| `abc` | `ABC`, `abstractmethod` — `AbstractComponent` base class |
| `typing` | Type hints throughout (`Literal`, `Any`, `list`, etc.) |
| `copy` | `copy.deepcopy` for default properties when instantiating components |
| `atexit` | Register cleanup handler to stop preview Conky on app exit |
| `os` | File permission checks, directory creation fallback |

---

## Development Dependencies

| Package | Usage |
|---|---|
| `pytest>=7.4` | Test runner |
| `pytest-cov>=4.1` | Coverage reporting |

---

## Optional / Future Dependencies (not required for v1)

| Package | Usage |
|---|---|
| `PyYAML` | If project format is ever extended to YAML (deferred) |
| `GtkSource` (GtkSourceView 5) | Syntax-highlighted Lua editor for `extra_lua` field (post-v1) |
| `pycairo` | In-app simulated preview renderer (post-v1) |
