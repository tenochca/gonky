"""Toolbar / HeaderBar — stub for Sub-Task 4."""
# Implemented in Sub-Task 4 (GUI Shell and Main Window Layout).

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class ToolBar(Gtk.HeaderBar):
    """Application header bar with New, Open, Save,
     Export, Preview, Apply, and Settings buttons.

     Each button emits a signal that MainWindow connects
     to business logic in later sub-tasks, currently wired to no-op stubs
     """

     def __init__(self) -> None:
        super().__init__()

    # Left Side: File actions

    self.btn_new = self._make_button("document-new-symbolic", "New project")
    self.btn_open = self._make_button("document-open-symbolic", "Open project")
    self.btn_save = self._make_button("document-save-symbolic", "Save project")

    for btn in (self.btn_new, self.btn_open, self.btn_save):
        self.pack_start(btn)
    