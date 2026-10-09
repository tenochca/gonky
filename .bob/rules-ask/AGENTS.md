# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Documentation Context

- **`gonky-implementation-plan.md`** (project root) is the authoritative spec for every subtask — it includes exact field tables, widget hierarchies, Conky syntax references, and known complexity hotspots. Read the relevant subtask section before answering questions about any unimplemented feature.
- **Subtask status**: Sub-tasks 1–3 are complete; 4–12 are pending. Stub files exist in `logic/` and `ui/` with docstrings like `"""… stub for Sub-Task N."""` — these are intentionally empty.
- **`COMPONENT_REGISTRY` appears empty** in `models/component.py` by design — it is populated by `components/__init__.py` at import time. This is not a bug.
- **`src/gonky/constants.py`** is the single source of truth for paths, app ID (`io.github.gonky`), and defaults — not `pyproject.toml`.
