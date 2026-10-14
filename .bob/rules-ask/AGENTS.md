# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Documentation Context

- **`gonky-implementation-plan.md`** (project root) is the authoritative spec for every subtask — it includes exact field tables, widget hierarchies, Conky syntax references, and known complexity hotspots. Read the relevant subtask section before answering questions about any unimplemented feature.
- **Sub-task status**: Sub-tasks 1–6 are complete (models, settings, all components, config generator, main window skeleton). Sub-tasks 7–12 are pending. Stub files in `logic/` and `ui/` contain only a docstring like `"""… stub for Sub-Task N."""` — these are intentionally empty.
- **`COMPONENT_REGISTRY` appears empty** in `models/component.py` by design — it is populated by `components/__init__.py` at import time. This is not a bug.
- **`src/gonky/constants.py`** is the single source of truth for paths, app ID (`io.github.gonky`), and defaults — not `pyproject.toml`.
- **`GlobalConkySettings` field names differ from Conky output keys**: `window_width` → `minimum_width`, `window_height` → `minimum_height`; font fields are combined as `font = 'Name:size=N'` in output.
- **`extra_lua`** in `GlobalConkySettings` is emitted between `conky.config {}` and `conky.text = [[` — it is not a Conky config key and does not appear inside the config block.
