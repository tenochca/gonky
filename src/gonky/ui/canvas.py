"""Canvas — Gtk.Fixed surface where component widgets are positioned."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from typing import Callable
from gonky.models.component import ConkyComponent


class Canvas(Gtk.ScrolledWindow):
    """Centre panel providing a scrollable, fixed-coordinate drawing surface.

    Sub-Task 4: renders a dark background with a placeholder label.
    Sub-Task 5: the Gtk.Fixed child will host draggable component widgets.
    Sub-Task 7: exposes on_component_selected / on_component_deselected hooks
                so MainWindow can forward selection to the PropertiesPanel.
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

        # Selection callbacks — set by MainWindow in Sub-Task 7.
        # on_component_selected(component) — called when a tile is clicked.
        # on_component_deselected()        — called when selection is cleared.
        self.on_component_selected: Callable[[ConkyComponent], None] | None = None
        self.on_component_deselected: Callable[[], None] | None = None

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

    def rebuild_from_document(self, doc: "GonkyDocument") -> None:  # type: ignore[name-defined]
        """Rebuild the canvas from *doc*.

        Full implementation is part of Sub-Task 5. This stub exists so that
        the file-management layer (Sub-Task 9) can call it without error.
        """

    def remove_placeholder(self) -> None:
        """Hide the placeholder once real components are present."""
        if self._placeholder is not None:
            self.fixed.remove(self._placeholder)
            self._placeholder = None

    def notify_selected(self, component: ConkyComponent) -> None:
        """Called by a component tile when it is clicked/selected."""
        if self.on_component_selected is not None:
            self.on_component_selected(component)

    def notify_deselected(self) -> None:
        """Called when the canvas background is clicked (selection cleared)."""
        if self.on_component_deselected is not None:
            self.on_component_deselected()
