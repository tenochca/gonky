# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Non-Obvious Coding Rules

- **Registry side-effect import**: Tests using `COMPONENT_REGISTRY` must `import gonky.components` (even as `# noqa: F401`) or the registry will be empty at test time — it's populated by `components/__init__.py` as a side effect, not by `models/component.py`. `ConfigGenerator` already does this internally; only standalone tests need it.
- **Sentinel values**: `0` means "use Conky default" for numeric dimensions/core selectors; `""` means "inherit" for color fields. Do not replace these with `None` — they get embedded directly in generated Conky config strings.
- **`gi.require_version` ordering**: Must appear before the `from gi.repository import ...` line. The `# noqa: E402` comment on the import line is intentional and required.
- **Layer enforcement**: `models/` and `logic/` and `components/` must never import from `gi.repository`. Violating this breaks testability (tests run headless without a display).
- **Path constants**: Import from `src/gonky/constants.py` (`ASSETS_DIR`, `STYLES_DIR`, `APP_CSS_PATH`, etc.) — do not construct paths inline.
- **Conky graph colors**: Both `color_lo` and `color_hi` must be set together or omitted together — Conky rejects one without the other. The `render_conky_text()` implementation must check both before emitting either.
- **`property_schema()` is a classmethod**: It returns `list[PropertyField]`. The `label` and `enabled` fields are NOT in `property_schema()` — they are prepended by the properties panel for every component. Every key in `property_schema()` must also appear in `DEFAULT_PROPERTIES` or the test suite will fail.
- **`Spacer` render contract**: `render_conky_text()` must return `'\n' * max(line_count, 1)` with **no extra trailing newline** — `ConfigGenerator._render_text_block()` appends it verbatim. All other components get `+ "\n"` appended by the generator.
- **Dollar-escaping scope**: Only `CustomText` user content goes through `_escape_conky_text()`. All other `render_conky_text()` outputs contain intentional `${...}` Conky syntax and must never be escaped.
- **Settings field-to-Conky key mapping**: `window_width` → `minimum_width`, `window_height` → `minimum_height`; `default_font`+`default_font_size` are combined as `font = 'Name:size=N'`. The Python field names must never appear in generated output.
- **`extra_lua` placement**: Goes between the closing `}` of `conky.config` and `conky.text = [[` — not inside `conky.config {}`. Omitted entirely when empty.
- **Sub-task stubs**: Files in `logic/` and `ui/` with `"""… stub for Sub-Task N."""` are intentionally empty. Do not add unrelated logic to them; implement each stub as its own sub-task.
