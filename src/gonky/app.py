"""GonkyApp — Gtk.Application subclass managing the application lifecycle."""

import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio  # noqa: E402

from gonky.constants import APP_ID, APP_NAME
from gonky.ui.main_window import MainWindow


class GonkyApp(Gtk.Application):
    """Top-level GTK 4 application object.

    Responsibilities:
    - Register the application with the desktop session (single-instance).
    - Create and present the main window on activation.
    - Wire up global application actions (quit, new, open, save, export).
    """

    def __init__(self) -> None:
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.connect("activate", self._on_activate)

    # ------------------------------------------------------------------
    # Private handlers
    # ------------------------------------------------------------------

    def _on_activate(self, _app: Gtk.Application) -> None:
        """Called by GTK when the application is first started (or re-activated)."""
        window = MainWindow(application=self)
        window.set_title(APP_NAME)
        window.present()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> int:  # type: ignore[override]
        """Start the GTK main loop. Returns exit code."""
        return super().run(sys.argv)
