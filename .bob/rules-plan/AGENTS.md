# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Architectural Constraints

- **Three-layer hard boundary**: `models/` → `logic/` → `ui/`. Lower layers must not import from higher ones. `components/` sits alongside `models/` and has zero GTK dependency. Breaking this makes headless unit testing impossible.
- **`COMPONENT_REGISTRY` is a shared mutable dict** in `models/component.py`, populated as a side effect of importing `components/__init__.py`. Any code path that needs the full registry (config generator, canvas, properties panel) must ensure `gonky.components` has been imported first — `app.py` is the natural place.
- **Canvas ordering → config ordering**: `canvas_y` (then `canvas_x`) determines output order in `conky.text`. The config generator (Sub-Task 6) owns this sort — the canvas does not reorder components. This means the visual layout drives the config, not the other way around.
- **Preview config override**: `PreviewManager` injects `alignment = 'top_right'` when generating the preview config, regardless of document settings — this prevents the preview Conky window from overlapping the Gonky window. The document is never mutated.
- **`GonkyDocument` is the single source of truth**: All panels hold a reference to `main_window.document` and call `main_window.on_document_changed()` after mutating it. Panels do not hold local copies of component state.
- **Sub-tasks 6 and 4 are independent** and can be implemented in parallel. Sub-task 6 (config generator) has zero GUI dependency. Sub-tasks 5, 7, 9 all require Sub-task 4 to be done first.
