# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Commands

```bash
# Run all tests
pytest

# Run a single test file
pytest tests/test_models.py

# Run a single test class or function
pytest tests/test_components.py::TestComponentRegistry::test_all_expected_keys_present

# Run with coverage
pytest --cov=src/gonky --cov-report=term-missing

# Run the app
python -m gonky
```

## Architecture: Three Hard Layers

**No GTK imports are allowed in `models/` or `logic/` — ever.** GTK lives only in `ui/` and `app.py`.

- `src/gonky/models/` — pure Python dataclasses, no GTK
- `src/gonky/logic/` — business logic (config gen, file I/O, process mgmt), no GTK
- `src/gonky/components/` — component definitions, no GTK
- `src/gonky/ui/` — all GTK widget code

## Component System

Adding a new component requires exactly 3 steps — no other files change:
1. Create a class in `src/gonky/components/<category>/` subclassing `AbstractComponent`
2. Set `TYPE_KEY`, `DISPLAY_NAME`, `ICON_NAME`, `DEFAULT_PROPERTIES`; implement `render_conky_text(self, props: dict) -> str` and `property_schema()`
3. Import the class in `src/gonky/components/__init__.py` and add `COMPONENT_REGISTRY[MyClass.TYPE_KEY] = MyClass`

`COMPONENT_REGISTRY` lives in `src/gonky/models/component.py` but is **populated** by `src/gonky/components/__init__.py`. Tests that use the registry must `import gonky.components` (even as `# noqa: F401`) to trigger this side-effect — without it, the registry is empty.

## GTK 4 Patterns

- `gi.require_version("Gtk", "4.0")` must be called **before** `from gi.repository import Gtk` — always in that order
- Use `Gtk.FileDialog` (async, GTK 4.10+) not `Gtk.FileChooserDialog`
- Use `Gtk.DropDown` + `Gtk.StringList` not `Gtk.ComboBoxText`
- DnD uses `Gtk.DragSource` / `Gtk.DropTarget` controllers attached to widgets (not methods on widgets)

## Code Style

- Module docstring on every file: `"""Short description."""`
- Type annotations on all function parameters and return types
- Inline comments on `DEFAULT_PROPERTIES` and dataclass fields explaining non-obvious semantics
- `0` as sentinel for "use Conky default" (width, height, core) — not `None`
- Empty string `""` as sentinel for "inherit/no override" on color fields — not `None`
- `pathlib.Path` for all filesystem paths — no `os.path` string joining

## Key Files

| File | Purpose |
|------|---------|
| `src/gonky/constants.py` | All paths (`ASSETS_DIR`, `STYLES_DIR`, etc.) and app identity (`APP_ID`) |
| `src/gonky/models/document.py` | `GonkyDocument`, `SchemaVersionError`, `_MIGRATIONS` registry |
| `src/gonky/components/__init__.py` | Canonical registry population — edit here when adding components |
| `gonky-implementation-plan.md` | Detailed per-subtask spec — read before implementing any subtask |
