# Manual Testing Checklist

This checklist covers manual QA steps to perform before each release, across supported
Linux distributions.

> **Note:** This document is a stub. Full checklist will be developed during Sub-Task 12
> (Polish, Documentation, and v1 Wrap-Up).

## Distributions to Test

- [ ] Ubuntu 22.04 LTS (GNOME)
- [ ] Ubuntu 24.04 LTS (GNOME)
- [ ] Fedora 40 (GNOME)
- [ ] Arch Linux (current)
- [ ] Debian 12 (GNOME)

## Test Scenarios

- [ ] Fresh install: `pip install -e .` works without errors
- [ ] App launches: `python -m gonky` opens main window
- [ ] Empty canvas: no errors on startup
- [ ] New project dialog
- [ ] Drag component to canvas
- [ ] Edit component properties
- [ ] Preview with Conky installed
- [ ] Preview without Conky installed (graceful error)
- [ ] Save project file (.gonky)
- [ ] Load project file (.gonky)
- [ ] Export config (.conf)
- [ ] Validation errors surface correctly
