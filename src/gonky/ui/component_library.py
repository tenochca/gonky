"""Component library panel — scrollable grouped list of available components."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, GObject, Gtk  # noqa: E402

import gonky.components  # noqa: F401 — populates COMPONENT_REGISTRY
from gonky.models.component import COMPONENT_REGISTRY


# Map the module-path category segment to human-readable header text.
_CATEGORY_LABELS: dict[str, str] = {
    "system": "System",
    "display": "Display",
    "advanced": "Advanced",
}


class ComponentLibrary(Gtk.ScrolledWindow):
    """Left-hand panel listing every available component grouped by category.

    Each row stores the component TYPE_KEY as row data so MainWindow can read
    which component was selected when a drag or double-click occurs.

    A :class:`Gtk.DragSource` controller is attached to each selectable row so
    that dragging a row onto the canvas delivers the component TYPE_KEY string
    as the DnD payload.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_min_content_width(200)
        self.add_css_class("component-library")

        self._list_box = Gtk.ListBox()
        self._list_box.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self._list_box.add_css_class("navigation-sidebar")
        self.set_child(self._list_box)

        self._populate()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _populate(self) -> None:
        """Insert header + item rows for each category."""
        # Group components by category derived from module path.
        groups: dict[str, list] = {}
        for component_cls in COMPONENT_REGISTRY.values():
            # __module__ is like "gonky.components.system.cpu"
            parts = component_cls.__module__.split(".")
            # parts[2] is the category segment: system / display / advanced
            category = parts[2] if len(parts) > 2 else "other"
            groups.setdefault(category, []).append(component_cls)

        ordered = list(_CATEGORY_LABELS.keys()) + [
            k for k in groups if k not in _CATEGORY_LABELS
        ]

        for category in ordered:
            if category not in groups:
                continue
            self._add_header(category)
            for cls in groups[category]:
                self._add_item(cls)

    def _add_header(self, category: str) -> None:
        """Insert a non-selectable bold section header row."""
        label = Gtk.Label(label=_CATEGORY_LABELS.get(category, category).upper())
        label.set_halign(Gtk.Align.START)
        label.set_margin_start(8)
        label.set_margin_top(6)
        label.set_margin_bottom(2)
        label.add_css_class("caption-heading")

        row = Gtk.ListBoxRow()
        row.set_selectable(False)
        row.set_activatable(False)
        row.set_child(label)
        self._list_box.append(row)

    def _add_item(self, component_cls) -> None:
        """Insert a selectable, draggable component row."""
        label = Gtk.Label(label=component_cls.DISPLAY_NAME)
        label.set_halign(Gtk.Align.START)
        label.set_margin_start(16)  # indented under header
        label.set_margin_top(4)
        label.set_margin_bottom(4)

        row = Gtk.ListBoxRow()
        row.set_child(label)
        # Stash the TYPE_KEY so MainWindow can retrieve it on selection.
        row.type_key = component_cls.TYPE_KEY

        # -- Drag source -------------------------------------------------
        # The DnD payload is the component TYPE_KEY string, wrapped in a
        # GObject.Value so Gdk.ContentProvider.new_for_value() can carry it.
        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.COPY)

        # Capture type_key in closure for prepare callback.
        type_key = component_cls.TYPE_KEY

        def on_prepare(source: Gtk.DragSource, _x: float, _y: float) -> Gdk.ContentProvider:
            value = GObject.Value()
            value.init(GObject.TYPE_STRING)
            value.set_string(type_key)
            return Gdk.ContentProvider.new_for_value(value)

        drag_source.connect("prepare", on_prepare)
        row.add_controller(drag_source)

        self._list_box.append(row)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_selected_type_key(self) -> str | None:
        """Return the TYPE_KEY of the currently selected row, or None."""
        row = self._list_box.get_selected_row()
        return getattr(row, "type_key", None)
