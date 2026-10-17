# Gonky — Manual Testing Checklist

This checklist covers the manual QA steps to perform before each release.
Automated tests (`pytest`) cover the data model, config generator, file manager, validator,
and component rendering. This checklist covers the GTK 4 GUI layer, which is not
exercised by the automated suite.

> **Automated GUI testing** via AT-SPI/Dogtail is a post-v1 item. All GUI QA is
> performed manually against this checklist.

---

## Distributions to Test

Perform the full checklist on each supported distribution before tagging a release:

- [ ] Ubuntu 22.04 LTS (GNOME 42, GTK 4.6)
- [ ] Fedora 38 (GNOME 44, GTK 4.10)
- [ ] Arch Linux (current stable, GTK 4.x latest)

---

## Pre-requisites

Before starting, verify the environment:

- [ ] Python 3.10+ is installed (`python3 --version`)
- [ ] PyGObject is installed (`python3 -c "import gi; print(gi.__version__)"`)
- [ ] Conky is installed (`conky --version`)
- [ ] Project is installed in editable mode (`pip install -e .`)
- [ ] Automated tests pass with zero failures (`pytest`)

---

## Test Scenarios

### 1 — Launch

- [ ] **1.1** Run `python -m gonky` — main window opens with no errors in stdout/stderr
- [ ] **1.2** Window title shows "Gonky — Untitled"
- [ ] **1.3** Left panel shows the component library list (all categories visible)
- [ ] **1.4** Centre area shows an empty canvas
- [ ] **1.5** Right panel shows an empty / placeholder properties area
- [ ] **1.6** Toolbar is visible with New, Open, Save, Export, Preview buttons

---

### 2 — Drag-and-Drop Canvas

- [ ] **2.1** Drag "CPU Bar" from the library to the canvas — a tile appears at the drop position
- [ ] **2.2** Drag a second component ("RAM Usage") to a different position — two tiles visible
- [ ] **2.3** Drag a tile that is already on the canvas to a new position — tile moves, no duplicate
- [ ] **2.4** Attempt to drag a component tile off the canvas edge — tile stays within bounds or
      behaves gracefully (no crash)
- [ ] **2.5** Drop two components at the same Y coordinate — both tiles visible, no overlap error

---

### 3 — Properties Panel

- [ ] **3.1** Click a canvas tile — the right panel populates with fields for that component type
- [ ] **3.2** Default values are shown in each field matching `DEFAULT_PROPERTIES` for that type
- [ ] **3.3** Change the "Width" field to `150` — value updates in the field
- [ ] **3.4** Click elsewhere on the canvas — value `150` persists when the same tile is clicked again
- [ ] **3.5** Change a colour field to `#ff0000` — value accepted without error
- [ ] **3.6** Enter an invalid colour (`#ZZZZZZ`) — a validation indicator appears on the field
- [ ] **3.7** Toggle the "Enabled" switch off — tile on canvas shows a disabled state
- [ ] **3.8** Click a different tile — properties panel updates to show that tile's fields

---

### 4 — Preview (requires Conky installed)

- [ ] **4.1** Click the Preview button — Conky appears on the desktop after a short delay
- [ ] **4.2** Conky overlay shows the components from the canvas in the correct order
- [ ] **4.3** Change a component colour to red — after ~1.5 s Conky auto-refreshes showing the change
- [ ] **4.4** Click Preview again while Conky is running — Conky reloads (not a second instance)
- [ ] **4.5** Close the app while Conky is previewing — Conky subprocess terminates cleanly
      (verify with `pgrep conky` returning nothing)

### 5 — Preview without Conky installed

- [ ] **5.1** Uninstall or rename the `conky` binary so `shutil.which("conky")` returns `None`
- [ ] **5.2** Click Preview — an informative error dialog appears ("Conky not found" or similar)
- [ ] **5.3** No crash; app continues to function after dismissing the dialog

---

### 6 — File → Save

- [ ] **6.1** File → Save — a file chooser dialog opens
- [ ] **6.2** Choose a location and save — a `.gonky` file is written to the chosen path
- [ ] **6.3** Open the saved file in a text editor — it is valid JSON containing
      `"schema_version": "1.0"` and the component list
- [ ] **6.4** Window title no longer shows the "unsaved changes" indicator after saving
- [ ] **6.5** Save to a path whose parent directory does not exist — directory is created automatically

---

### 7 — File → New

- [ ] **7.1** With unsaved changes on the canvas, File → New — a "Save changes?" dialog appears
- [ ] **7.2** Choose "Discard" — canvas clears, title resets to "Gonky — Untitled"
- [ ] **7.3** Choose "Save" — file chooser appears; after saving, canvas clears
- [ ] **7.4** Choose "Cancel" — new project is aborted, canvas retains its content
- [ ] **7.5** File → New on a fresh (unmodified) document — canvas clears immediately, no dialog

---

### 8 — File → Open

- [ ] **8.1** File → Open — file chooser opens filtered to `.gonky` files
- [ ] **8.2** Select a previously saved `.gonky` file — canvas reconstructs all tiles at their
      saved positions
- [ ] **8.3** Properties panel shows correct values for each loaded component
- [ ] **8.4** Select a file with an unsupported `schema_version` — an error dialog appears
      ("Unsupported schema version" or similar); app does not crash
- [ ] **8.5** Select a corrupt (non-JSON) file — an error dialog appears; app does not crash

---

### 9 — File → Export Config

- [ ] **9.1** File → Export Config — a file chooser opens, defaulting to
      `~/.config/conky/conky.conf`
- [ ] **9.2** Confirm — a `.conf` file is written to the chosen path
- [ ] **9.3** Open the exported file — it starts with `conky.config = {` and contains
      `conky.text = [[`
- [ ] **9.4** Parent directory (`~/.config/conky/`) is created automatically if it did not exist
- [ ] **9.5** In a terminal, run `conky -c <exported_path>` — Conky renders with the correct layout

---

### 10 — Validation and Error Feedback

- [ ] **10.1** Add an "Exec Command" component, leave the command field empty, click Export —
       an error dialog lists "Command must not be empty"
- [ ] **10.2** Open Global Settings, set Update Interval to `0`, close — validation error shown
- [ ] **10.3** Set a network interface to `"eth 0"` (with a space) — validation error shown on
       the interface field
- [ ] **10.4** Correct all errors — Export proceeds without the error dialog

---

### 11 — Global Settings Dialog

- [ ] **11.1** Open Global Settings (via menu or toolbar) — dialog shows all fields with defaults
- [ ] **11.2** Change alignment to `bottom_right`, save — exported config contains
      `alignment = 'bottom_right'`
- [ ] **11.3** Change font to `Noto Mono`, size to `12` — exported config contains
      `font = 'Noto Mono:size=12'`
- [ ] **11.4** Close dialog without saving — previous values are retained

---

### 12 — End-to-End Conky Rendering

Performed on each target distribution:

- [ ] **12.1** Build a layout with at least: CPU Bar, RAM Usage, Separator, Clock, Custom Text
- [ ] **12.2** Export config to `~/.config/conky/conky.conf`
- [ ] **12.3** Run `conky -c ~/.config/conky/conky.conf` in a terminal
- [ ] **12.4** Conky overlay appears on the desktop with all five components visible
- [ ] **12.5** Custom text content appears without any spurious `$` or `\$` characters
- [ ] **12.6** No Conky errors in the terminal output

---

## Sign-off

After completing all checks on all required distributions, record results here:

| Distribution | Tester | Date | Result |
|---|---|---|---|
| Ubuntu 22.04 LTS | | | ☐ Pass / ☐ Fail |
| Fedora 38 | | | ☐ Pass / ☐ Fail |
| Arch Linux | | | ☐ Pass / ☐ Fail |
