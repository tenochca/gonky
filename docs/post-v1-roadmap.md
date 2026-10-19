# Post-v1.0.0 Roadmap

Features deferred from the v1 milestone.

## Deferred Features

### In-App Simulated Preview Pane
- Render a visual approximation of the Conky overlay directly inside the app using
  Cairo/Pango rendering, without spawning a Conky subprocess.
- Would remove the subprocess dependency for preview entirely.

### Drag-to-Resize Component Tiles
- Allow users to resize component tiles on the canvas by dragging their edges or
  corners, reflecting a custom width/height in the generated config.

### Undo/Redo History
- Implement a command pattern on all document mutations so every canvas action
  (add, move, delete, property change) is reversible.
- Standard Ctrl+Z / Ctrl+Shift+Z bindings.

### Theme Import/Export
- Allow exporting the current `GlobalConkySettings` as a `.gonkytheme` JSON file
  and importing it into any project for quick visual consistency.

### Import Existing `conky.conf`
- Parse an existing `~/.config/conky/conky.conf` and reconstruct an approximate
  Gonky document from it, lowering the barrier for existing Conky users.

### Conky Variable Scripting Editor
- Embed a GtkSourceView 5 (`GtkSource`) editor for the `extra_lua` field with
  Lua syntax highlighting.
- Dependency: `python3-gtksourceview5` or `pip install PyGObject[GtkSource]`.

### Multi-Monitor Support
- Let the user choose which physical monitor the Conky overlay targets when
  generating positional settings (`gap_x`, `gap_y`, `xinerama_head`).

### Auto-Detect Network Interfaces and Block Devices
- Populate network-interface and block-device dropdowns in the properties panel
  automatically by reading `/sys/class/net/` and `/proc/partitions` at startup.

### Snap Desktop Wallpaper as Canvas Background
- Capture a screenshot of the current wallpaper and display it as a faint
  background behind the canvas to help users position overlays accurately.

### Automated GUI Testing via AT-SPI/Dogtail
- Use the AT-SPI2 accessibility bus and the `dogtail` library to write automated
  UI-level tests covering click, drag, and keyboard interactions.

### Packaging
- `.deb` package for Debian/Ubuntu via `stdeb` or `dpkg-buildpackage`.
- `.rpm` package for Fedora/openSUSE.
- Flatpak manifest for cross-distro installation via Flathub.
- AUR PKGBUILD for Arch Linux users.
