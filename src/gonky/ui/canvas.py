"""Canvas — Gtk.Fixed surface where component widgets are positioned."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class Canvas(Gtk.ScrolledWindow):
    """Centre panel providing a scrollable, fixed-coordinate drawing surface.

    Sub-Task 4: renders a dark background with a placeholder label.
    Sub-Task 5: the Gtk.Fixed child will host draggable component widgets.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("canvas-scroll")

        # Gtk.Fixed is the coordinate surface — components are placed at (x, y).
        self.fixed = Gtk.Fixed()
        self.fixed.set_hexpand(True)
        self.fixed.set_vexpand(True)
        self.fixed.add_css_class("canvas")
        self.set_child(self.fixed)

        self._placeholder = self._make_placeholder()
        self.fixed.put(self._placeholder, 0, 0)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_placeholder() -> Gtk.Label:
        """Return the placeholder label shown before any components are added."""
        label = Gtk.Label(label="Drop components here")
        label.set_hexpand(True)
        label.set_vexpand(True)
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        label.add_css_class("dim-label")
        label.add_css_class("canvas-placeholder")
        return label

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def remove_placeholder(self) -> None:
        """Hide the placeholder once real components are present."""
        if self._placeholder is not None:
            self.fixed.remove(self._placeholder)
            self._placeholder = None
