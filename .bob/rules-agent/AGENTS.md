# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Coding Rules

- **Registry side-effect import**: Tests using `COMPONENT_REGISTRY` must `import gonky.components` (even as `# noqa: F401`) or the registry will be empty at test time — it's populated by `components/__init__.py` as a side effect, not by `models/component.py`.
- **Sentinel values**: `0` means "use Conky default" for numeric dimensions/core selectors; `""` means "inherit" for color fields. Do not replace these with `None` — they get embedded directly in generated Conky config strings.
- **`gi.require_version` ordering**: Must appear before the `from gi.repository import ...` line. The `# noqa: E402` comment on the import line is intentional and required.
- **Layer enforcement**: `models/` and `logic/` and `components/` must never import from `gi.repository`. Violating this breaks testability (tests run headless without a display).
- **Path constants**: Import from `src/gonky/constants.py` (`ASSETS_DIR`, `STYLES_DIR`, `APP_CSS_PATH`, etc.) — do not construct paths inline.
- **Conky graph colors**: Both `color_lo` and `color_hi` must be set together or omitted together — Conky rejects one without the other. The `render_conky_text()` implementation must check both before emitting either.
- **`property_schema()` is a classmethod**: It returns `list[PropertyField]`. The `label` and `enabled` fields are NOT in `property_schema()` — they are prepended by the properties panel for every component.
