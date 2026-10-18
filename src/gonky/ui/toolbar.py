"""Toolbar / HeaderBar — stub for Sub-Task 4."""
# Implemented in Sub-Task 4 (GUI Shell and Main Window Layout).

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class ToolBar(Gtk.HeaderBar):
    """Application header bar with New, Open, Save,
     Export, Preview, and Settings buttons.

     Each button emits a signal that MainWindow connects
     to business logic in later sub-tasks, currently wired to no-op stubs
     """

    def __init__(self) -> None:
        super().__init__()

        # Left Side: File actions

        self.btn_new = self._make_button("document-new-symbolic", "New project (Ctrl+N)")
        self.btn_open = self._make_button("document-open-symbolic", "Open project (Ctrl+O)")
        self.btn_save = self._make_button("document-save-symbolic", "Save project (Ctrl+S)")

        for btn in (self.btn_new, self.btn_open, self.btn_save):
            self.pack_start(btn)

        # Right Side: Workflow actions

        self.btn_settings = self._make_button("emblem-system-symbolic", "Global settings")
        self.btn_preview = self._make_toggle("view-refresh-symbolic", "Toggle live preview (Ctrl+P)")
        self.btn_export = self._make_button("document-send-symbolic", "Export Conky config (Ctrl+E)")

        for btn in (self.btn_settings, self.btn_preview, self.btn_export):
            self.pack_end(btn)


    # Helpers

    @staticmethod
    def _make_button(icon_name: str, tooltip: str) -> Gtk.Button:
        "return a flat icon button"
        btn = Gtk.Button()
        btn.set_icon_name(icon_name)
        btn.set_tooltip_text(tooltip)
        btn.add_css_class("flat")
        return btn

    @staticmethod
    def _make_toggle(icon_name: str, tooltip: str) -> Gtk.ToggleButton:
        "return a flat icon toggle button"
        btn = Gtk.ToggleButton()
        btn.set_icon_name(icon_name)
        btn.set_tooltip_text(tooltip)
        btn.add_css_class("flat")
        return btn