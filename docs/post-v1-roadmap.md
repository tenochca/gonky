# Post-v1 Roadmap

Features deferred from the v1 milestone.

## Deferred Features

### Syntax-Highlighted Lua Editor
- Use GtkSourceView 5 (`GtkSource`) to provide a syntax-highlighted editor for the
  `extra_lua` field on components with inline Lua blocks.
- Dependency: `python3-gtksourceview5` or `pip install PyGObject[GtkSource]`.

### In-App Simulated Preview Renderer
- Render a visual approximation of the Conky overlay directly inside the app using
  `pycairo`, without requiring Conky to be installed.
- Would remove the subprocess dependency for preview entirely.

### YAML Project Format
- Optionally support `.gonky.yaml` project files in addition to `.gonky` (JSON) for
  human-editability. Would add `PyYAML` dependency.

### Rust Rewrite (gtk-rs)
- After v1 feature-freeze, a Rust rewrite using `gtk-rs` / `relm4` is a viable option
  for improved startup time and binary distribution.

### Flatpak / AppImage Packaging
- Package Gonky as a Flatpak for easy cross-distro installation via Flathub.
- AppImage as an alternative for offline distribution.

### Component Import/Export
- Allow individual components (with their property sets) to be exported as reusable
  `.gonky-component` snippets and shared between projects.

### Theme Presets
- Ship a set of built-in CSS theme presets (dark, light, minimal, retro) selectable
  from the preferences dialog.
