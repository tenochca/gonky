"""Canvas — Gtk.Fixed surface where component widgets are positioned."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GLib, GObject, Gtk  # noqa: E402

import gonky.components  # noqa: F401 — populates COMPONENT_REGISTRY
from gonky.models.component import COMPONENT_REGISTRY, ConkyComponent


class CanvasTile(Gtk.Box):
    """Visual representation of one ConkyComponent on the canvas.

    Displays the component display name in a small card.  Visual selection
    state is communicated via the ``canvas-tile-selected`` CSS class
    (added/removed by :meth:`set_selected`).

    Minimum size is enforced at 120×40 px as per the tile visual spec.
    """

    def __init__(self, component: ConkyComponent, display_name: str) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.component = component  # live reference — mutated by canvas operations
        self.set_size_request(120, 40)
        self.add_css_class("canvas-tile")

        # Icon label (text-based icon placeholder)
        self._icon_label = Gtk.Label(label="⬜")
        self._icon_label.add_css_class("canvas-tile-icon")
        self._icon_label.set_valign(Gtk.Align.CENTER)

        # Component display name
        self._name_label = Gtk.Label(label=display_name)
        self._name_label.add_css_class("canvas-tile-label")
        self._name_label.set_valign(Gtk.Align.CENTER)
        self._name_label.set_halign(Gtk.Align.START)
        self._name_label.set_ellipsize(3)  # PANGO_ELLIPSIZE_END = 3

        self.append(self._icon_label)
        self.append(self._name_label)

        self.set_selected(False)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def set_selected(self, selected: bool) -> None:
        """Toggle the selected visual state (CSS class + border colour)."""
        if selected:
            self.add_css_class("canvas-tile-selected")
            self.remove_css_class("canvas-tile-unselected")
        else:
            self.add_css_class("canvas-tile-unselected")
            self.remove_css_class("canvas-tile-selected")


class Canvas(Gtk.ScrolledWindow):
    """Centre panel providing a scrollable, fixed-coordinate drawing surface.

    Hosts a :class:`Gtk.Fixed` child onto which :class:`CanvasTile` widgets
    are placed at (canvas_x, canvas_y) coordinates stored in each
    :class:`~gonky.models.component.ConkyComponent`.

    The canvas holds a reference to the parent :class:`MainWindow` (set after
    construction via :attr:`main_window`) so it can read/write the document
    and call ``on_document_changed()``.

    A :class:`Gtk.DropTarget` on the :class:`Gtk.Fixed` child accepts
    ``GObject.TYPE_STRING`` drops from the component library, creates a new
    :class:`ConkyComponent`, and adds a :class:`CanvasTile` at the drop
    coordinates.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.add_css_class("canvas-scroll")

        # Back-reference to MainWindow — wired up after construction.
        self.main_window = None  # type: ignore[assignment]

        # tile_map: component id -> CanvasTile, for O(1) lookup
        self._tile_map: dict[str, CanvasTile] = {}

        # Gtk.Fixed is the coordinate surface — components are placed at (x, y).
        self.fixed = Gtk.Fixed()
        self.fixed.set_hexpand(True)
        self.fixed.set_vexpand(True)
        self.fixed.add_css_class("canvas")
        self.set_child(self.fixed)

        self._placeholder: Gtk.Label | None = self._make_placeholder()
        self.fixed.put(self._placeholder, 0, 0)

        # Wire up drop target for library → canvas drops.
        self._setup_drop_target()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _make_placeholder() -> Gtk.Label:
        """Return the placeholder label shown before any components are added."""
        label = Gtk.Label(
            label=(
                "Drop components here\n"
                "Components are output top-to-bottom in order of "
                "their vertical position on the canvas."
            )
        )
        label.set_hexpand(True)
        label.set_vexpand(True)
        label.set_halign(Gtk.Align.CENTER)
        label.set_valign(Gtk.Align.CENTER)
        label.set_justify(Gtk.Justification.CENTER)
        label.add_css_class("dim-label")
        label.add_css_class("canvas-placeholder")
        return label

    def _hide_placeholder(self) -> None:
        """Remove the placeholder once real components are present."""
        if self._placeholder is not None:
            self.fixed.remove(self._placeholder)
            self._placeholder = None

    def _show_placeholder_if_empty(self) -> None:
        """Re-add the placeholder label when the canvas becomes empty."""
        if self._tile_map:
            return
        if self._placeholder is None:
            self._placeholder = self._make_placeholder()
        self.fixed.put(self._placeholder, 0, 0)

    def _setup_drop_target(self) -> None:
        """Attach a Gtk.DropTarget to the Gtk.Fixed for library → canvas drops."""
        drop_target = Gtk.DropTarget.new(GObject.TYPE_STRING, Gdk.DragAction.COPY)
        drop_target.connect("drop", self._on_library_drop)
        self.fixed.add_controller(drop_target)

    def _on_library_drop(
        self,
        _target: Gtk.DropTarget,
        value: str,
        x: float,
        y: float,
    ) -> bool:
        """Handle a drop from the component library.

        Creates a new :class:`ConkyComponent` of the dropped type, appends it
        to the document, and places a :class:`CanvasTile` at the drop point.
        Returns True to indicate the drop was accepted.
        """
        type_key: str = value
        component_cls = COMPONENT_REGISTRY.get(type_key)
        if component_cls is None:
            return False

        canvas_x = int(x)
        canvas_y = int(y)

        # Build the new component with default properties.
        component = ConkyComponent(
            component_type=type_key,
            label=component_cls.DISPLAY_NAME,
            canvas_x=canvas_x,
            canvas_y=canvas_y,
            properties=dict(component_cls.DEFAULT_PROPERTIES),
        )

        # Persist to document.
        if self.main_window is not None:
            self.main_window.document.components.append(component)
            self.main_window.on_document_changed()

        # Create and place the tile.
        tile = CanvasTile(component, component_cls.DISPLAY_NAME)
        self.add_tile(tile, canvas_x, canvas_y)
        return True

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def remove_placeholder(self) -> None:
        """Hide the placeholder once real components are present (legacy API)."""
        self._hide_placeholder()

    def add_tile(self, tile: "CanvasTile", x: int, y: int) -> None:
        """Place *tile* on the fixed surface at (*x*, *y*) and register it."""
        self._hide_placeholder()
        self._tile_map[tile.component.id] = tile
        self.fixed.put(tile, x, y)

    def move_tile(self, component_id: str, x: int, y: int) -> None:
        """Move an existing tile to the new canvas coordinates."""
        tile = self._tile_map.get(component_id)
        if tile is None:
            return
        self.fixed.move(tile, x, y)
        tile.component.canvas_x = x
        tile.component.canvas_y = y

    def remove_tile(self, component_id: str) -> None:
        """Remove the tile for *component_id* from the canvas."""
        tile = self._tile_map.pop(component_id, None)
        if tile is not None:
            self.fixed.remove(tile)
        self._show_placeholder_if_empty()

    def get_tile(self, component_id: str) -> "CanvasTile | None":
        """Return the tile for *component_id*, or None if not present."""
        return self._tile_map.get(component_id)

    def deselect_all(self) -> None:
        """Remove the selected CSS class from every tile."""
        for tile in self._tile_map.values():
            tile.set_selected(False)
