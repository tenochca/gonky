"""Properties panel — scrolled container for the component property form."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class PropertiesPanel(Gtk.ScrolledWindow):
    """Right-hand panel displaying properties for the selected component.

    Sub-Task 4: shows a 'No component selected' placeholder.
    Sub-Task 7: the form_builder will replace the placeholder with live fields.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_min_content_width(280)
        self.add_css_class("properties-panel")

        self._content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        self.set_child(self._content_box)

        self._show_placeholder()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _show_placeholder(self) -> None:
        """Render the 'No component selected' empty state."""
        label = Gtk.Label(label="No component selected")
        label.set_vexpand(True)
        label.set_hexpand(True)
        label.set_valign(Gtk.Align.CENTER)
        label.set_halign(Gtk.Align.CENTER)
        label.add_css_class("dim-label")
        self._content_box.append(label)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all children from the content box (used by Sub-Task 7)."""
        child = self._content_box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._content_box.remove(child)
            child = next_child
