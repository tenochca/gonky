# Gonky — Conky GUI Configuration Front-End: Implementation Plan

## Top-Level Overview

**Goal:** Build a desktop GUI application called *Gonky* that lets users visually compose a Conky layout using a drag-and-drop canvas, configure each component through a properties panel, and export a syntactically correct Lua-based Conky config file. The app must also be able to start, stop, and reload Conky directly.

**Scope:** Full application from scratch — data model, GUI shell, component system, config generator, preview system, project persistence, and Conky process management.

**Approach:** Python 3 + GTK 4 via PyGObject. The application is structured in three clearly separated layers:

1. **Data layer** — pure Python dataclasses; no GUI imports
2. **Business logic layer** — config generation, file I/O, process management, validation
3. **GUI layer** — GTK widgets, canvas, property forms, dialogs

**Key decisions:**
- Language/framework: Python 3 + GTK 4 (PyGObject) — full justification in Sub-Task 1
- Canvas: drag-and-drop visual canvas (v1 complexity accepted; ordered-list fallback noted as risk mitigation)
- Preview: launch a real Conky instance pointing at a temp config (recommended v1 approach)
- Project file format: JSON
- Distribution: run from source for v1

---

## Sub-Task 1 — Technology Stack, Project Structure, and Scaffolding

### Intent
Establish the foundation: justify the technology choices with full rationale (including why Python is preferred over C++ despite Conky being written in C++), define the full directory tree, create all stub files, and configure the project so a developer can `git clone` and run immediately.

### Expected Outcomes
- `README.md` documents how to install dependencies and run the app
- `pyproject.toml` / `requirements.txt` lists all dependencies with version pins
- Full directory tree exists with stub files (no logic yet, just structure)
- App launches with an empty main window and no errors

### Todo List
1. Finalise and document technology stack justification in `docs/tech-stack.md`
2. Create `pyproject.toml` with project metadata and entry point
3. Create `requirements.txt` and `requirements-dev.txt`
4. Create the full directory tree (see Relevant Context below)
5. Write `src/gonky/__main__.py` — entry point: `python -m gonky`
6. Write `src/gonky/app.py` — `Gtk.Application` subclass, lifecycle management
7. Write stub `src/gonky/ui/main_window.py` — `Gtk.ApplicationWindow` subclass, empty layout
8. Write `README.md` — setup, dependencies, how to run
9. Verify `python -m gonky` launches without errors

### Relevant Context

---

#### Language Choice: Python 3

**Gonky does not interact with Conky's source code.** Although Conky itself is written in C++, Gonky's only integration surface with Conky is a plain-text `.conf` file and a shell process (`conky -c <path>`). There is no `libconky` API to bind against and no shared data structures to exchange. The language choice is therefore purely a GUI development productivity decision.

**Why not C++?**

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

**When C++ would be the right choice:** if Gonky needed to link against a native Conky library, perform real-time system-level rendering, or ship as a size-constrained system utility with no interpreter. None of these apply.

**Why not Rust (gtk-rs)?** Rust + GTK 4 via `gtk-rs` is a modern, high-quality option. Rejected for v1 because the learning curve for Rust ownership semantics combined with GTK 4's callback-heavy API is a significant productivity tax on a first-version GUI application. Post-v1 rewrite is viable.

**Why not Qt (PyQt6 / PySide6)?** PyQt6 carries GPL/commercial licensing nuance. PySide6 (LGPL) is fine but adds a heavier dependency that is not pre-installed on most Linux desktops. GTK 4 is the native Linux toolkit and is already present on GNOME-based distributions.

**Why not Electron/Tauri?** Electron adds ~200 MB of Node.js/Chromium overhead. Tauri (Rust + WebView) is lighter but inherits the Rust complexity concern above. Neither produces a native Linux look-and-feel.

**Verdict: Python 3.10+ with GTK 4 via PyGObject.**

---

#### GUI Framework: GTK 4 via PyGObject

- `PyGObject` — Python bindings for GLib/GObject/GTK 4. Install via `pip install PyGObject` or distro package `python3-gi`. Minimum version: PyGObject 3.42 (GTK 4.6+).
- `Gtk.Application` — application lifecycle, single-instance enforcement, action registration
- `Gtk.ApplicationWindow` — main window
- `Gtk.Fixed` — free-position canvas container for drag-and-drop component placement
- `Gtk.DragSource` / `Gtk.DropTarget` — GTK 4 drag-and-drop API (replaces the deprecated GTK 3 `drag_source_set` / `drag_dest_set`)
- `Gtk.ListBox` — component library panel
- `Gtk.SpinButton`, `Gtk.Entry`, `Gtk.Switch`, `Gtk.ColorButton`, `Gtk.DropDown`, `Gtk.FontButton` — property form widgets
- `Gtk.Paned` — resizable panel splitter
- `Gtk.CssProvider` — load `assets/styles/gonky.css` for visual theming
- `Gtk.FileDialog` — GTK 4 async file chooser (replaces `Gtk.FileChooserDialog`)
- `Gtk.MessageDialog` — error and confirmation dialogs
- `GLib.timeout_add` — debounce timer for preview refresh

#### Core Python Standard Library Modules

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

#### Development Dependencies

| Package | Usage |
|---|---|
| `pytest` | Test runner |
| `pytest-cov` | Coverage reporting |

#### Optional / Future Dependencies (not required for v1)

| Package | Usage |
|---|---|
| `PyYAML` | If project format is ever extended to YAML (deferred) |
| `GtkSource` (GtkSourceView 5) | Syntax-highlighted Lua editor for `extra_lua` field (post-v1) |
| `pycairo` | In-app simulated preview renderer (post-v1) |

---

#### Proposed Directory Tree

```
gonky/
├── pyproject.toml                  # Build metadata, entry points, tool config
├── requirements.txt                # Runtime dependencies (PyGObject pin)
├── requirements-dev.txt            # pytest, pytest-cov
├── README.md
├── docs/
│   ├── tech-stack.md               # Full technology choice rationale (this section)
│   ├── conky-variables-reference.md # Supported Conky vars and their syntax
│   ├── manual-testing-checklist.md # Checklist for manual QA across distros
│   └── post-v1-roadmap.md          # Deferred features
├── assets/
│   ├── icons/
│   │   ├── gonky.svg               # App icon
│   │   └── components/             # Per-component-type icons (SVG, 24x24)
│   └── styles/
│       └── gonky.css               # GTK CSS overrides
├── src/
│   └── gonky/
│       ├── __init__.py
│       ├── __main__.py             # Entry point: python -m gonky
│       ├── app.py                  # Gtk.Application subclass, lifecycle
│       ├── constants.py            # App-wide constants (paths, version, defaults)
│       │
│       ├── models/                 # DATA LAYER — zero GTK imports allowed
│       │   ├── __init__.py
│       │   ├── component.py        # ConkyComponent dataclass + COMPONENT_REGISTRY
│       │   ├── document.py         # GonkyDocument dataclass (full session state)
│       │   └── settings.py         # GlobalConkySettings dataclass
│       │
│       ├── logic/                  # BUSINESS LOGIC LAYER — zero GTK imports allowed
│       │   ├── __init__.py
│       │   ├── config_generator.py # GonkyDocument → Lua config string
│       │   ├── file_manager.py     # Save/load .gonky JSON, export .conf
│       │   ├── preview_manager.py  # Manages the live Conky preview subprocess
│       │   ├── process_manager.py  # Conky install detection, start/stop/reload
│       │   └── validator.py        # Input validation, pre-export checks
│       │
│       ├── ui/                     # GUI LAYER — GTK imports here only
│       │   ├── __init__.py
│       │   ├── main_window.py      # GtkApplicationWindow, panel assembly
│       │   ├── canvas.py           # Drag-and-drop canvas (Gtk.Fixed + tiles)
│       │   ├── component_library.py # Left panel: browseable component type list
│       │   ├── properties_panel.py  # Right panel: dynamic property form
│       │   ├── toolbar.py          # HeaderBar with action buttons
│       │   ├── statusbar.py        # Bottom status bar + Conky state indicator
│       │   ├── form_builder.py     # Shared PropertyField → Gtk.Widget factory
│       │   └── dialogs/
│       │       ├── __init__.py
│       │       ├── new_project.py  # New project name prompt
│       │       ├── save_load.py    # Gtk.FileDialog wrappers
│       │       ├── export.py       # Export config dialog
│       │       ├── global_settings.py # GlobalConkySettings editor
│       │       ├── error_dialog.py # Scrollable validation error list
│       │       └── about.py        # About dialog
│       │
│       └── components/             # COMPONENT DEFINITIONS
│           ├── __init__.py         # Imports all components, builds registry
│           ├── base.py             # AbstractComponent + PropertyField dataclass
│           ├── system/
│           │   ├── __init__.py
│           │   ├── cpu.py          # CpuUsage, CpuBar, CpuGraph, CpuFreq, LoadAvg
│           │   ├── memory.py       # RamUsage, RamBar, RamGraph, SwapUsage
│           │   ├── disk.py         # DiskUsage, DiskBar, DiskIo, DiskIoGraph
│           │   ├── network.py      # NetUpload, NetDownload, NetUploadGraph, NetDownloadGraph, NetIp
│           │   ├── battery.py      # BatteryPercent, BatteryBar, BatteryTime
│           │   └── temperature.py  # Temperature
│           ├── display/
│           │   ├── __init__.py
│           │   ├── clock.py        # Clock, Date, Uptime
│           │   ├── text.py         # CustomText
│           │   ├── spacer.py       # Spacer
│           │   ├── separator.py    # Separator
│           │   ├── graph.py        # GenericGraph
│           │   └── bar.py          # GenericBar, Processes, ProcessCount
│           └── advanced/
│               ├── __init__.py
│               ├── lua_snippet.py  # RawLuaSnippet
│               └── exec.py         # ExecCommand
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_config_generator.py
    ├── test_file_manager.py
    ├── test_validator.py
    └── test_integration.py
```

### Status
- [ ] pending

---

## Sub-Task 2 — Data Model

### Intent
Define all Python dataclasses that represent the internal state of the application. This is the contract between every other layer — the GUI reads from and writes to these objects; the config generator reads from them exclusively.

### Expected Outcomes
- All dataclasses defined in `src/gonky/models/`
- Unit tests pass for model creation, serialisation to dict, and deserialisation from dict
- No GTK imports in any model file

### Todo List
1. Implement `GlobalConkySettings` dataclass in `models/settings.py` — all fields documented inline
2. Implement `ConkyComponent` dataclass in `models/component.py` — all fields documented inline
3. Implement the component type registry (`COMPONENT_REGISTRY`) in `models/component.py` — maps `component_type` string to the concrete component class
4. Implement `GonkyDocument` dataclass in `models/document.py` — holds `GlobalConkySettings` + ordered list of `ConkyComponent`
5. Add `to_dict()` / `from_dict()` class methods on `GonkyDocument` (JSON round-trip)
6. Write `tests/test_models.py` covering construction, defaults, dict round-trip, and `SchemaVersionError`

### Relevant Context

**`GlobalConkySettings` fields**

| Field | Type | Default | Maps to Conky config key |
|---|---|---|---|
| `alignment` | str | `top_left` | `conky.config.alignment` |
| `gap_x` | int | 10 | `conky.config.gap_x` |
| `gap_y` | int | 10 | `conky.config.gap_y` |
| `window_width` | int | 300 | `conky.config.minimum_width` |
| `window_height` | int | 0 | `conky.config.minimum_height` (0 = auto) |
| `own_window` | bool | True | `conky.config.own_window` |
| `own_window_type` | str | `desktop` | `conky.config.own_window_type` |
| `own_window_transparent` | bool | True | `conky.config.own_window_transparent` |
| `own_window_argb_visual` | bool | True | `conky.config.own_window_argb_visual` |
| `double_buffer` | bool | True | `conky.config.double_buffer` |
| `update_interval` | float | 1.0 | `conky.config.update_interval` |
| `default_font` | str | `DejaVu Sans Mono` | `conky.config.font` (name part) |
| `default_font_size` | int | 10 | `conky.config.font` (size part) |
| `default_color` | str | `white` | `conky.config.default_color` |
| `background` | bool | False | `conky.config.background` |
| `border_width` | int | 0 | `conky.config.border_width` |
| `cpu_avg_samples` | int | 2 | `conky.config.cpu_avg_samples` |
| `net_avg_samples` | int | 2 | `conky.config.net_avg_samples` |
| `extra_lua` | str | `` | raw Lua appended at end of config block |

**`ConkyComponent` fields**

| Field | Type | Description |
|---|---|---|
| `id` | str | UUID4, generated on creation |
| `component_type` | str | Registry key, e.g. `"cpu_bar"` |
| `label` | str | User-visible name in canvas tile |
| `canvas_x` | int | Pixel X position on canvas |
| `canvas_y` | int | Pixel Y position on canvas |
| `enabled` | bool | If False, skipped during config generation |
| `properties` | dict | Type-specific key/value pairs (defined per component class) |

**`GonkyDocument` fields**

| Field | Type | Description |
|---|---|---|
| `schema_version` | str | `"1.0"` — forward compatibility hook |
| `project_name` | str | User-visible project name |
| `settings` | GlobalConkySettings | Global Conky config block values |
| `components` | list[ConkyComponent] | All components placed on canvas |

**JSON serialisation strategy:** `to_dict()` uses `dataclasses.asdict()` recursively. `from_dict()` checks `schema_version` and raises `SchemaVersionError` if the version is not supported. A migration registry (keyed by version string) allows future schema upgrades — for v1 the registry is empty since only `"1.0"` exists.

### Status
- [ ] pending

---

## Sub-Task 3 — Component System

### Intent
Define all supported Conky component types as concrete classes. Each class declares its configurable properties, default values, Conky variable mappings, and config-text rendering logic. The design makes the system self-describing and trivially extensible.

### Expected Outcomes
- All v1 component classes implemented in `src/gonky/components/`
- Each component passes its own unit test for `render_conky_text()` output
- Adding a new component requires only: creating a new file, defining one class, and registering one string key — no other files change

### Todo List
1. Define `AbstractComponent` and `PropertyField` in `components/base.py`
2. Implement all system components: cpu, memory, disk, network, battery, temperature
3. Implement all display components: clock, text, spacer, separator, graph, bar
4. Implement advanced components: lua_snippet, exec
5. Register every component in `COMPONENT_REGISTRY` in `models/component.py`
6. Write unit tests for each component's `render_conky_text()` output

### Relevant Context

**`AbstractComponent` interface** (defined in `components/base.py`):

```
class AbstractComponent(ABC):
    TYPE_KEY: str               # Registry key, e.g. "cpu_bar"
    DISPLAY_NAME: str           # Human label shown in the component library panel
    ICON_NAME: str              # Filename stem in assets/icons/components/
    DEFAULT_PROPERTIES: dict    # Shallow-copied on each instantiation

    @abstractmethod
    def render_conky_text(self, props: dict) -> str:
        """Return the conky.text fragment for this component instance."""

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        """Return ordered PropertyField list — used by form_builder to auto-generate
        the properties panel UI."""
```

**`PropertyField` descriptor** (used by `form_builder.py` to generate property form widgets automatically):

```
@dataclass
class PropertyField:
    key: str
    label: str
    field_type: Literal["text", "int", "float", "bool", "color", "choice", "font"]
    default: Any
    choices: list[str] | None = None   # Only used when field_type="choice"
    min_val: float | None = None       # Only used for int/float
    max_val: float | None = None       # Only used for int/float
    tooltip: str = ""
```

**V1 Component Catalogue**

| Category | Type Key | Display Name | Key Properties | Conky Variables/Syntax |
|---|---|---|---|---|
| **System** | `cpu_usage` | CPU Usage % | core (int/all), color | `${cpu cpu0}` |
| | `cpu_bar` | CPU Bar | core, width, height, color | `${cpubar cpu0 h,w}` |
| | `cpu_graph` | CPU Graph | core, width, height, color_lo, color_hi | `${cpugraph cpu0 h,w color1 color2}` |
| | `cpu_freq` | CPU Frequency | core | `${freq_g N}` |
| | `load_avg` | Load Average | period (1/5/15) | `${loadavg N}` |
| | `ram_usage` | RAM Usage | format (%, bytes, human) | `${mem}` / `${memperc}` |
| | `ram_bar` | RAM Bar | width, height, color | `${membar h,w}` |
| | `ram_graph` | RAM Graph | width, height, color_lo, color_hi | `${memgraph h,w c1 c2}` |
| | `swap_usage` | Swap Usage | format | `${swap}` / `${swapperc}` |
| | `disk_usage` | Disk Usage | mount_point, format | `${fs_used /}` / `${fs_free /}` / `${fs_used_perc /}` |
| | `disk_bar` | Disk Bar | mount_point, width, height | `${fs_bar h,w /}` |
| | `disk_io` | Disk I/O | device, direction | `${diskio_read sda}` / `${diskio_write sda}` |
| | `disk_io_graph` | Disk I/O Graph | device, direction, width, height | `${diskiograph_read sda h,w}` |
| | `net_upload` | Net Upload Speed | interface | `${upspeed eth0}` |
| | `net_download` | Net Download Speed | interface | `${downspeed eth0}` |
| | `net_upload_graph` | Net Upload Graph | interface, width, height, colors | `${upspeedgraph eth0 h,w c1 c2}` |
| | `net_download_graph` | Net Download Graph | interface, width, height, colors | `${downspeedgraph eth0 h,w c1 c2}` |
| | `net_ip` | IP Address | interface | `${addr eth0}` |
| | `battery_percent` | Battery % | battery_id | `${battery_percent BAT0}` |
| | `battery_bar` | Battery Bar | battery_id, width, height | `${battery_bar h,w BAT0}` |
| | `battery_time` | Battery Time Remaining | battery_id | `${battery_time BAT0}` |
| | `temperature` | Temperature | hwmon path or thermal zone, unit | `${hwmon N temp N}` or `${exec cat /sys/.../temp1_input}` |
| | `processes` | Top Processes | count, sort_by (cpu/mem) | `${top name N}` / `${top cpu N}` / `${top mem N}` |
| | `process_count` | Process Count | | `${running_processes}` / `${processes}` |
| **Display** | `clock` | Clock | format string | `${time %H:%M:%S}` |
| | `date` | Date | format string | `${time %Y-%m-%d}` |
| | `uptime` | Uptime | | `${uptime}` |
| | `text` | Custom Text | text content, color, font, size | Literal string in `conky.text` |
| | `spacer` | Spacer | line_count | `\n` × count |
| | `separator` | Separator Line | width, color | `${hr N}` |
| | `bar` | Generic Bar | variable_expr, width, height | `${bar h,w variable}` |
| | `graph` | Generic Graph | variable_expr, width, height, colors | `${graph variable h,w c1 c2}` |
| **Advanced** | `exec` | Shell Command | command, exec_type (exec/execbar/execgraph) | `${exec command}` / `${execbar}` / `${execgraph}` |
| | `lua_snippet` | Raw Conky/Lua Text | raw_text | Literal injection into `conky.text` |

**Extensibility contract:** To add a new component after v1:
1. Create a new file in the appropriate `components/` subdirectory
2. Subclass `AbstractComponent`: fill in `TYPE_KEY`, `DISPLAY_NAME`, `ICON_NAME`, `DEFAULT_PROPERTIES`; implement `render_conky_text()` and `property_schema()`
3. Import the class in `components/__init__.py` and add it to `COMPONENT_REGISTRY`

No other files need modification.

### Status
- [x] complete

---

## Sub-Task 4 — GUI Shell and Main Window Layout

### Intent
Build the application's main window with all panels in their correct structural positions but with placeholder/stub content. Establish the GTK widget hierarchy, the CSS theming hook, and the inter-panel communication pattern used throughout the app.

### Expected Outcomes
- Main window renders with correct panel layout (toolbar top, library left, canvas centre, properties right, status bar bottom)
- Resizing the window resizes the canvas area; side panels maintain fixed minimum widths
- GTK CSS stylesheet loads and applies
- All panels have placeholder widgets
- No business logic wired yet

### Todo List
1. Implement `ui/toolbar.py` — `Gtk.HeaderBar` with icon buttons: New, Open, Save, Export Config, Preview Toggle, Apply to Conky, Settings
2. Implement `ui/statusbar.py` — `Gtk.Statusbar` with message area and Conky running/stopped indicator label
3. Implement `ui/component_library.py` — `Gtk.ScrolledWindow` + `Gtk.ListBox` grouped by category; stub items only
4. Implement `ui/properties_panel.py` — `Gtk.ScrolledWindow` + `Gtk.Box` with "No component selected" placeholder
5. Implement `ui/canvas.py` — stub `Gtk.Fixed` with placeholder label
6. Assemble all panels in `ui/main_window.py` using nested `Gtk.Paned`
7. Load `assets/styles/gonky.css` via `Gtk.CssProvider` in `app.py`
8. Implement `ui/dialogs/about.py`
9. Verify layout renders correctly at 800×600, 1280×800, and 1920×1080 window sizes

### Relevant Context

**Main window layout (logical):**

```
┌───────────────────────────────────────────────────────────────┐
│  HeaderBar  [New] [Open] [Save] [Export] [Preview] [Apply] [⚙] │
├──────────────┬────────────────────────────┬────────────────────┤
│ Component    │                            │ Properties Panel   │
│ Library      │         Canvas             │ (280px fixed)      │
│ (200px fixed)│   (flex — fills space)     │                    │
│              │                            │ ScrolledWindow     │
│ ScrolledWindow│   Gtk.Fixed               │ + dynamic form     │
│ + ListBox    │   dark background          │                    │
│              │                            │                    │
├──────────────┴────────────────────────────┴────────────────────┤
│  StatusBar  [message text]                [● Conky: stopped]   │
└───────────────────────────────────────────────────────────────┘
```

**GTK widget hierarchy:**

```
Gtk.ApplicationWindow
  └─ Gtk.Box (vertical, spacing=0)
       ├─ Gtk.HeaderBar
       ├─ Gtk.Paned (horizontal, start_child=ComponentLibrary, position=200)
       │    └─ Gtk.Paned (horizontal, end_child=PropertiesPanel, position=-280)
       │         └─ Canvas (Gtk.Fixed, hexpand=True, vexpand=True)
       └─ Gtk.Statusbar
```

**Inter-panel communication pattern:** All panels receive a reference to `MainWindow` on construction. They read and write `main_window.document` (the `GonkyDocument`) directly. After any mutation, they call `main_window.on_document_changed()` which (a) sets the dirty flag, (b) updates the window title, and (c) triggers the preview debounce. This avoids circular panel dependencies and keeps the document as the single source of truth.

### Status
- [ ] pending

---

## Sub-Task 5 — Drag-and-Drop Canvas

### Intent
Implement the interactive canvas where users drag components from the library onto a free-position area, move them around, select them (populating the properties panel), and delete them.

### Expected Outcomes
- Dragging a component type from the library onto the canvas creates a new `ConkyComponent` and renders a positioned `CanvasTile`
- Tiles can be dragged to new positions; `canvas_x`/`canvas_y` update in the document
- Clicking a tile selects it and signals the properties panel to update
- Delete key removes the selected tile and its document entry
- `canvas.rebuild_from_document()` correctly reconstructs all tiles from a loaded document

### Todo List
1. Implement `CanvasTile` widget in `ui/canvas.py` — `Gtk.Frame` or `Gtk.Box` showing component icon + label, with selected/unselected visual state via CSS class
2. Implement drag source on `ComponentLibrary` list rows using `Gtk.DragSource` — payload is `component_type` string via `Gdk.ContentProvider.new_for_value()`
3. Implement drop target on `Canvas` using `Gtk.DropTarget` — on drop, create `ConkyComponent` via `COMPONENT_REGISTRY`, add to document, create and position `CanvasTile` at drop coordinates
4. Implement tile drag-move — `Gtk.DragSource` on each `CanvasTile`, `Gtk.DropTarget` on the `Gtk.Fixed`; update `canvas_x`/`canvas_y` on drop completion
5. Implement selection — `Gtk.GestureClick` on each `CanvasTile`; clicking sets `main_window.selected_component_id`, emits signal to refresh properties panel; clicking blank canvas deselects
6. Implement keyboard delete — `Gtk.EventControllerKey` on `Canvas`; Delete key removes selected component from document, destroys tile
7. Implement `canvas.rebuild_from_document(doc: GonkyDocument)` — clears all tiles, creates one `CanvasTile` per component at stored coordinates
8. Implement z-order bring-to-front on selection — `fixed.remove(tile)` then `fixed.put(tile, x, y)` to ensure selected tile renders on top

### Relevant Context

**⚠️ Complexity hotspot — GTK 4 DnD API:** GTK 4 replaced the GTK 3 DnD API entirely. `Gtk.DragSource` and `Gtk.DropTarget` are controllers attached to widgets (not methods on widgets). Payload transfer uses `Gdk.ContentProvider` and `GObject.Value`. Prototype the full DnD round-trip in an isolated test script before integrating into the main canvas to avoid debugging in the full application context.

**⚠️ Canvas-to-conky.text ordering constraint:** Conky's text block is strictly linear (top-to-bottom). Free-position canvas coordinates must be sorted by Y (then X as tiebreaker) to determine the output order. This sort happens in the config generator (Sub-Task 6), not here. Display a persistent tooltip or info bar on the canvas: *"Components are output top-to-bottom in order of their vertical position on the canvas."*

**Tile visual spec:** Minimum size 120×40px. Canvas background colour `#1e1e2e` (dark, simulates a desktop). Selected tile border: `2px solid #89b4fa`. Unselected tile border: `1px solid #45475a`.

### Status
- [ ] pending

---

## Sub-Task 6 — Config File Generation Engine

### Intent
Implement the pure-logic module that translates a `GonkyDocument` into a valid Conky Lua config file string. No GTK dependency; fully unit-testable.

### Expected Outcomes
- `ConfigGenerator.generate(doc)` returns a valid Lua config string for any valid `GonkyDocument`
- Output always contains `conky.config = {` and `conky.text = [[`
- All `GlobalConkySettings` fields render correctly in the config block
- Components render in Y-sort order (ascending Y, X as tiebreaker)
- All 30+ component types produce correct Conky variable syntax
- Escaping edge cases handled: literal `$` and `${` in custom text, empty component list
- Unit tests cover every component type and multiple global setting combinations

### Todo List
1. Implement `ConfigGenerator` class in `logic/config_generator.py` with static method `generate(doc: GonkyDocument) -> str`
2. Implement `_render_config_block(settings: GlobalConkySettings) -> str` — builds the Lua table literal
3. Implement `_sort_components(components: list[ConkyComponent]) -> list[ConkyComponent]` — sort by `canvas_y` then `canvas_x`
4. Implement `_render_text_block(components: list[ConkyComponent]) -> str` — iterates sorted enabled components, calls `render_conky_text()`, joins with `\n`
5. Implement `_escape_conky_text(text: str) -> str` — escapes `\$` for literal dollars in custom text components
6. Implement `_validate_before_generate(doc: GonkyDocument) -> list[str]` — pre-flight check; raises `ConfigGenerationError` if errors found
7. Write `tests/test_config_generator.py` — one test per component type, global settings rendering, Y-sort ordering, escaping edge cases, empty document

### Relevant Context

**Conky Lua config file structure:**

```lua
conky.config = {
    alignment = 'top_left',
    gap_x = 10,
    gap_y = 10,
    minimum_width = 300,
    minimum_height = 0,
    own_window = true,
    own_window_type = 'desktop',
    own_window_transparent = true,
    own_window_argb_visual = true,
    double_buffer = true,
    update_interval = 1.0,
    font = 'DejaVu Sans Mono:size=10',
    default_color = 'white',
    background = false,
    border_width = 0,
    cpu_avg_samples = 2,
    net_avg_samples = 2,
}

conky.text = [[
${color white}CPU Usage: ${cpu cpu0}%
${cpubar 4,200}
${membar 4,200}
]]
```

**Lua type mapping:**
- Python `True` → `true`, `False` → `false`
- Python `str` → single-quoted Lua string: `'value'`
- Python `int` / `float` → unquoted numeric literal

**Font string:** `conky.config.font` = `'FontName:size=N'`. The generator concatenates `settings.default_font + ":size=" + str(settings.default_font_size)`.

**⚠️ Escaping risk:** `$` inside `conky.text` introduces a Conky variable. Literal dollar signs in custom text must be written as `\$`. Custom text components that the user has typed `${` into must have the brace escaped to `\${`. Implement `_escape_conky_text()` with explicit unit tests for:
- `"costs $5"` → `"costs \$5"`
- `"value ${foo}"` → `"value \${foo}"`
- `"${cpu}"` passed as a raw variable → must NOT be escaped (only `text` component values are escaped; raw variable strings from component definitions are never passed through `_escape_conky_text`)

**Y-sort and linear output:** Components at the same Y are output left-to-right on the same visual line. The generator does not insert explicit X-positioning (Conky has no horizontal cursor movement). Document this as a known v1 limitation in both the UI tooltip and `docs/conky-variables-reference.md`.

### Status
- [ ] pending

---

## Sub-Task 7 — Properties Panel and Form Builder

### Intent
Implement the right-side properties panel that auto-generates a GTK form for the selected component's properties using the `PropertyField` descriptors from `property_schema()`. Changes must immediately update the document.

### Expected Outcomes
- Selecting a tile on the canvas populates the panel with the correct typed fields
- Each `PropertyField.field_type` renders the correct widget (see mapping below)
- Changing any field value writes to `component.properties[key]` immediately
- Deselecting shows the "No component selected" placeholder
- The Global Settings dialog reuses the same `form_builder.py` factory

### Todo List
1. Implement `ui/form_builder.py` — `make_field_widget(field: PropertyField, current_value, on_change: Callable) -> Gtk.Widget` factory
2. Map `field_type` to GTK widget: `text` → `Gtk.Entry`, `int`/`float` → `Gtk.SpinButton`, `bool` → `Gtk.Switch`, `color` → `Gtk.ColorButton`, `choice` → `Gtk.DropDown`, `font` → `Gtk.FontButton`
3. Implement `PropertiesPanel.show_component(component: ConkyComponent)` — clears panel, calls `component.property_schema()`, builds form via `form_builder`
4. Wire `changed` / `value-changed` / `notify::active` / `color-set` / `font-set` signals to write back to `component.properties[key]` and call `main_window.on_document_changed()`
5. Implement `PropertiesPanel.clear()` — shows placeholder message
6. Add `label` (text) and `enabled` (bool) as the first two rows in every component form (always present, not part of `property_schema()`)
7. Implement `ui/dialogs/global_settings.py` — reuses `form_builder.make_field_widget()` for `GlobalConkySettings` fields
8. Implement `ui/dialogs/error_dialog.py` — scrollable dialog displaying a list of `ValidationError` objects

### Relevant Context

**Color storage:** `Gtk.ColorButton` returns `Gdk.RGBA`. Store as hex string `"#rrggbb"` in `properties`. Conky accepts `#rrggbb` directly in `${color}` directives.

**Font storage:** `Gtk.FontButton` returns a Pango font description string (e.g. `"DejaVu Sans Mono 10"`). Store as-is. The config generator parses this into `name:size=N` format when rendering per-component font overrides.

**`Gtk.DropDown` for choice fields:** GTK 4 replaced `Gtk.ComboBoxText` with `Gtk.DropDown`. Use `Gtk.StringList` as the model and set the selected index from the current value.

**`Gtk.SpinButton` bounds:** Set `Gtk.Adjustment(value, min_val, max_val, step, page, 0)` from `PropertyField.min_val` / `PropertyField.max_val`. This enforces numeric bounds without manual validation code.

### Status
- [ ] pending

---

## Sub-Task 8 — Preview System

### Intent
Implement the live preview that launches a real Conky instance using the current document's generated config.

### Expected Outcomes
- Clicking the Preview toolbar button starts Conky with the current generated config
- Clicking Preview again stops it; toolbar button state reflects running/stopped
- Editing a property triggers a 1.5s debounce, then auto-refreshes the preview
- If Conky is not installed, a clear `Gtk.MessageDialog` explains the situation
- The preview Conky process is terminated on application exit

### Todo List
1. Implement `logic/process_manager.py`:
   - `is_conky_installed() -> bool` — uses `shutil.which("conky")`
   - `start_conky(config_path: Path) -> subprocess.Popen` — runs `conky -c <path> --daemonize`
   - `stop_conky(proc: subprocess.Popen)` — SIGTERM, 3s wait, SIGKILL fallback
   - `is_running(proc: subprocess.Popen) -> bool` — `proc.poll() is None`
2. Implement `logic/preview_manager.py`:
   - `PreviewManager` holds current `Popen` handle and temp config path (`~/.cache/gonky/preview.conf`)
   - `start_preview(doc: GonkyDocument)` — generates preview config (with forced `top_right` alignment override), writes to temp path, calls `process_manager.start_conky()`
   - `stop_preview()` — calls `process_manager.stop_conky()` on current handle
   - `refresh_preview(doc: GonkyDocument)` — `stop_preview()` then `start_preview(doc)`
   - `schedule_refresh(doc: GonkyDocument)` — resets a `GLib.timeout_add(1500, ...)` debounce timer
3. Wire toolbar Preview button toggle to `preview_manager.start_preview()` / `stop_preview()`
4. Call `preview_manager.schedule_refresh()` from `main_window.on_document_changed()` when preview is active
5. Register `atexit.register(preview_manager.stop_preview)` in `app.py`
6. Show `Gtk.MessageDialog` when `is_conky_installed()` returns `False`

### Relevant Context

**Recommended v1 approach: real Conky subprocess.** Rationale: renders pixel-perfect output with live system data, zero rendering engine duplication, no divergence risk between preview and actual output. The 1–2s startup latency per refresh is acceptable with the 1.5s debounce.

**Alternative rejected for v1 — in-app simulated preview:** Would require reimplementing Conky's text renderer (fonts, colors, bars, graphs) using Cairo/Pango in Python. Weeks of extra work with high divergence risk. Deferred to post-v1 as an optional embedded preview pane.

**Preview config override:** When generating the preview config, inject `alignment = 'top_right'` and `gap_x = 10`, `gap_y = 10` regardless of document settings. This prevents the preview Conky window from overlapping the Gonky application window. The user's document settings are not modified.

**Conflict with existing Conky instance:** If the user is already running a Conky instance without `--config`, Conky's single-instance behaviour may cause the preview to fail silently. Document this in the UI as a tooltip on the Preview button: *"Preview launches a separate Conky instance. If Conky is already running without --config, you may need to stop it first."*

### Status
- [ ] pending

---

## Sub-Task 9 — Save, Load, and Export System

### Intent
Implement the project persistence layer: saving and loading GUI sessions as JSON files, and exporting final Conky Lua config files to user-chosen paths.

### Expected Outcomes
- File → Save writes a `.gonky` JSON file that round-trips perfectly
- File → Open reads a `.gonky` file, validates schema version, and rebuilds the canvas
- File → Export Config writes a `.conf` Lua file to a user-chosen path via `Gtk.FileDialog`
- Unsaved changes trigger a "Save before closing?" dialog on quit
- All file errors surface through `Gtk.MessageDialog`

### Todo List
1. Implement `logic/file_manager.py`:
   - `save_project(doc: GonkyDocument, path: Path)` — writes `json.dumps(doc.to_dict(), indent=2)` with `.gonky` extension
   - `load_project(path: Path) -> GonkyDocument` — reads JSON, calls `GonkyDocument.from_dict()`, raises `SchemaVersionError` on version mismatch
   - `export_config(doc: GonkyDocument, path: Path)` — calls `ConfigGenerator.generate(doc)`, writes string to file, creates parent dirs if needed
   - `get_default_export_path() -> Path` — returns `Path.home() / ".config" / "conky" / "conky.conf"`
2. Implement `ui/dialogs/save_load.py` — async `Gtk.FileDialog` wrappers for Save, Open, and Export; file filters for `.gonky` and `.conf`
3. Implement dirty-state tracking in `MainWindow` — `is_dirty: bool` flag, set in `on_document_changed()`, cleared in `save_project()`; window title shows `*` when dirty
4. Implement close/quit guard — override `Gtk.Window.close_request` signal; if `is_dirty`, show `Gtk.MessageDialog` with Save / Discard / Cancel
5. Implement `ui/dialogs/new_project.py` — prompts for project name, creates blank `GonkyDocument`, calls `canvas.rebuild_from_document()`
6. Wire all toolbar buttons to the corresponding dialog and `file_manager` functions
7. Write `tests/test_file_manager.py` — save+load round-trip, export output structural check, missing directory auto-creation, schema version mismatch error

### Relevant Context

**`.gonky` JSON structure:**

```json
{
  "schema_version": "1.0",
  "project_name": "My Desktop",
  "settings": {
    "alignment": "top_left",
    "gap_x": 10,
    "update_interval": 1.0
  },
  "components": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "component_type": "cpu_bar",
      "label": "CPU Bar",
      "canvas_x": 10,
      "canvas_y": 80,
      "enabled": true,
      "properties": {
        "core": "all",
        "width": 200,
        "height": 4,
        "color": "#ffffff"
      }
    }
  ]
}
```

**Forward compatibility:** `schema_version` is checked on `from_dict()`. If the loaded version is higher than the app's supported version, raise `SchemaVersionError` with a user-friendly message. If lower, apply the appropriate migration function from the migration registry. For v1, the registry is empty.

**Default export path:** `~/.config/conky/conky.conf`. Prompt the user to confirm before overwriting an existing file.

### Status
- [ ] pending

---

## Sub-Task 10 — Validation and Error Handling

### Intent
Implement input validation across the app so users get immediate actionable feedback, and so the config generator never writes a broken file to disk.

### Expected Outcomes
- Numeric `Gtk.SpinButton` fields reject out-of-range values automatically via `Gtk.Adjustment` bounds
- The Export and Apply actions run `Validator.validate(doc)` before proceeding; errors block the action
- Validation errors are shown in a scrollable list dialog with severity icons
- No unhandled Python exception reaches the user — all are caught and shown as `Gtk.MessageDialog`

### Todo List
1. Implement `logic/validator.py` — `Validator.validate(doc: GonkyDocument) -> list[ValidationError]`
2. Define `ValidationError` dataclass: `field: str`, `component_id: str | None`, `message: str`, `severity: Literal["error", "warning"]`
3. Implement per-field validators:
   - `validate_color(value: str) -> bool` — regex `^(#[0-9a-fA-F]{3,6}|0x[0-9a-fA-F]{6}|[a-zA-Z]+)$`; warn on unknown named colours but only block on structurally invalid strings
   - `validate_interval(value: float) -> bool` — must be >= 0.1
   - `validate_font(value: str) -> bool` — non-empty string
   - `validate_mount_point(value: str) -> bool` — must start with `/`
   - `validate_network_interface(value: str) -> bool` — non-empty, no whitespace
   - `validate_command(value: str) -> bool` — non-empty string (no deeper shell validation in v1)
4. Implement global settings validators: `window_width >= 0`, `gap_x >= 0`, `gap_y >= 0`, `update_interval >= 0.1`
5. Wire `Validator.validate()` into the Export and Apply toolbar actions — show `error_dialog.py` if any errors with `severity="error"`; show warning dialog for warnings-only (user can proceed)
6. Write `tests/test_validator.py`

### Relevant Context

**`Gtk.SpinButton` as first-line defence:** Setting bounds via `Gtk.Adjustment(value, lower, upper, step, page, 0)` from `PropertyField.min_val`/`max_val` prevents most numeric range errors without custom code.

**⚠️ Colour validation permissiveness:** Conky accepts many colour formats. Overly strict validation will frustrate users. The regex above is permissive — it allows any alphabetic string (named colours). Only structurally malformed strings (e.g. `"#ZZZZZZ"` or `"not valid 123"`) are blocked.

### Status
- [ ] pending

---

## Sub-Task 11 — Testing

### Intent
Implement the full automated test suite. GUI testing is limited to manual testing via checklist for v1.

### Expected Outcomes
- `pytest` runs with zero failures and zero errors
- Config generator tested for every component type
- File manager round-trip test confirms identical `GonkyDocument` after save+load
- Integration test confirms a multi-component document produces a structurally valid Lua config
- Coverage > 80% on `models/`, `logic/`, and `components/`

### Todo List
1. Set up `pytest` and `pytest-cov` in `requirements-dev.txt`; add `[tool.pytest.ini_options]` in `pyproject.toml`
2. Write `tests/test_models.py` — construction, defaults, `to_dict()`, `from_dict()`, `SchemaVersionError`
3. Write `tests/test_config_generator.py` — one test per component type, global settings block rendering, Y-sort ordering, escaping edge cases, empty and disabled-component documents
4. Write `tests/test_file_manager.py` — save+load round-trip, export structural check, missing parent directory creation, schema version mismatch
5. Write `tests/test_validator.py` — valid and invalid colours, interval bounds, empty project name, mount point format
6. Write `tests/test_integration.py` — construct a `GonkyDocument` with 5 mixed components, call `ConfigGenerator.generate()`, write via `FileManager.export_config()`, read back the file and assert that `conky.config = {`, `conky.text = [[`, and each component's expected Conky variable string are present
7. Document `docs/manual-testing-checklist.md` (see Relevant Context)

### Relevant Context

**Manual testing checklist (to write as `docs/manual-testing-checklist.md`):**
1. Launch app — window opens, no errors in stdout/stderr
2. Drag "CPU Bar" from library to canvas — tile appears at drop position
3. Click tile — properties panel shows CPU Bar fields with correct defaults
4. Change width to 150 — value persists when clicking elsewhere on canvas
5. Click Preview — Conky appears on screen
6. Change color to red — auto-refresh after 1.5s shows red bar
7. File → Save — `.gonky` file written to chosen path
8. File → New — canvas clears with "Save changes?" prompt if dirty
9. File → Open — loads saved file, canvas reconstructs all tiles at correct positions
10. File → Export Config — `.conf` written to `~/.config/conky/conky.conf`
11. In terminal: `conky -c ~/.config/conky/conky.conf` — Conky renders with correct layout
12. Repeat on Ubuntu 22.04, Fedora 38, Arch Linux (latest stable)

**GUI automation note:** Automated GUI testing via AT-SPI/Dogtail is not included in v1. It is a post-v1 item.

### Status
- [ ] pending

---

## Sub-Task 12 — Polish, Documentation, and v1 Wrap-Up

### Intent
Finalize the app for a usable v1 state: tooltips, keyboard shortcuts, app icon, complete documentation, and the post-v1 roadmap.

### Expected Outcomes
- All toolbar buttons have `tooltip_text` set
- All keyboard shortcuts work: Ctrl+N, Ctrl+O, Ctrl+S, Ctrl+E, Ctrl+P, Delete, Ctrl+Q
- App icon renders in taskbar and window chrome
- `README.md` is complete with install instructions and usage guide
- `docs/post-v1-roadmap.md` exists and lists all deferred features
- `pytest` passes; `python -m gonky` smoke test passes

### Todo List
1. Add `tooltip_text` to every toolbar button and `PropertyField` tooltip to every form row
2. Register keyboard shortcuts via `Gtk.Application.set_accels_for_action()` for New, Open, Save, Export, Preview, Quit; Delete handled via `Gtk.EventControllerKey` on canvas
3. Set app icon: `Gtk.Window.set_default_icon_name("gonky")` + install `assets/icons/gonky.svg` into the XDG icon theme path at `~/.local/share/icons/hicolor/scalable/apps/gonky.svg` or reference it directly via `Gtk.IconTheme.add_search_path()`
4. Write `docs/post-v1-roadmap.md` (see Relevant Context)
5. Write final `README.md` — system requirements, `pip install PyGObject` / `sudo apt install python3-gi` note, `python -m gonky` run command, feature overview, known limitations (Y-sort, no undo, no import of existing configs), license
6. Run `pytest --cov=src/gonky --cov-report=term-missing` — ensure > 80% coverage, zero failures
7. Run `python -m gonky` — smoke test the full happy path manually

### Relevant Context

**Post-v1 Roadmap (for `docs/post-v1-roadmap.md`):**
- In-app simulated preview pane (Cairo/Pango rendering, no subprocess)
- Drag-to-resize component tiles on canvas
- Undo/redo history (command pattern on document mutations)
- Theme import/export (`.gonkytheme` JSON for `GlobalConkySettings`)
- Import existing `conky.conf` and reconstruct approximate GUI state
- Conky variable scripting editor with syntax highlighting (GtkSourceView 5)
- Multi-monitor support (target monitor selection)
- Auto-detect network interfaces and block devices for dropdown population
- Snap of real desktop wallpaper as canvas background
- Automated GUI testing via AT-SPI/Dogtail
- Packaging: `.deb`, `.rpm`, Flatpak manifest, AUR PKGBUILD

### Status
- [ ] pending

---

## Cross-Cutting Technical Risks

| Risk | Severity | Mitigation |
|---|---|---|
| GTK 4 DnD API complexity in PyGObject | High | Prototype DnD in an isolated script before integrating; pin `PyGObject >= 3.42` |
| Canvas Y-sort → linear conky.text mismatch surprises users | Medium | Persistent info tooltip on canvas; document in README known limitations |
| Conky version variations across distros | Medium | Test on Conky >= 1.12 (Ubuntu 20.04 baseline); document minimum version in README |
| Preview Conky conflicting with user's existing Conky instance | Medium | Document in Preview button tooltip; no auto-kill of existing Conky processes |
| `$` / `${` escaping in custom text components | Medium | Dedicated unit tests for `_escape_conky_text()`; tooltip on the Custom Text component |
| PyGObject version fragmentation across distros | Low | Document `pip install PyGObject` as fallback; test on each target distro |
| `Gtk.FileDialog` async API (GTK 4.10+) vs older `Gtk.FileChooserDialog` | Low | Check available GTK version at runtime; fall back to `Gtk.FileChooserDialog` if GTK < 4.10 |
