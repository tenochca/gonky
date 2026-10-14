# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Architectural Constraints

- **Three-layer hard boundary**: `models/` → `logic/` → `ui/`. Lower layers must not import from higher ones. `components/` sits alongside `models/` and has zero GTK dependency. Breaking this makes headless unit testing impossible.
- **`COMPONENT_REGISTRY` is a shared mutable dict** in `models/component.py`, populated as a side effect of importing `components/__init__.py`. Any code path that needs the full registry (config generator, canvas, properties panel) must ensure `gonky.components` has been imported first — `app.py` is the natural place. `ConfigGenerator` imports it explicitly at module level.
- **Canvas ordering → config ordering**: `canvas_y` (then `canvas_x`) determines output order in `conky.text`. The config generator owns this sort — the canvas does not reorder components. Visual layout drives config, not the other way around. Disabled components (`enabled=False`) are excluded from output entirely.
- **`Spacer` newline contract breaks the uniform render pattern**: All components except `Spacer` get `+ "\n"` appended by `_render_text_block()`. `Spacer.render_conky_text()` returns raw `\n * line_count` and is appended verbatim — do not add a trailing newline in the Spacer implementation.
- **Dollar-escaping is type-gated**: `_escape_conky_text()` is called only for `component_type == "text"` (CustomText). Every other component's `render_conky_text()` output contains intentional Conky `${...}` syntax that must survive unescaped into the final file.
- **`extra_lua` layout**: Between `conky.config = { ... }` closing brace and `conky.text = [[`, separated by blank lines on each side. Omitted entirely when empty — no extra blank lines are inserted.
- **`GlobalConkySettings` field-to-key mapping**: `window_width`/`window_height` → `minimum_width`/`minimum_height`; `default_font`+`default_font_size` → single `font = 'Name:size=N'`. Generated config must never contain the Python field names.
- **`GonkyDocument` is the single source of truth**: All panels hold a reference to `main_window.document` and call `main_window.on_document_changed()` after mutating it. Panels do not hold local copies of component state.
- **Sub-tasks 7–12 are pending**: `logic/file_manager.py`, `logic/preview_manager.py`, `logic/process_manager.py`, `logic/validator.py`, `ui/form_builder.py` are all intentional stubs. Sub-task 6 (config generator) has zero GUI dependency and is done. Sub-tasks 5, 7, 9 all require Sub-task 4 to be completed first (4 is done).
