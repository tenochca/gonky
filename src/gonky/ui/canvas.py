"""Canvas — Gtk.Fixed surface where component widgets are positioned."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, GObject, Gtk  # noqa: E402

import gonky.components  # noqa: F401 — populates COMPONENT_REGISTRY
from gonky.models.component import COMPONENT_REGISTRY, ConkyComponent
from gonky.models.document import GonkyDocument

# Prefix used to distinguish tile-move DnD payloads from library-item payloads.
_TILE_DRAG_PREFIX = "tile:"


class CanvasTile(Gtk.Box):
    """Visual representation of one ConkyComponent on the canvas.

    Displays the component display name in a small card.  Visual selection
    state is communicated via the ``canvas-tile-selected`` CSS class
    (added/removed by :meth:`set_selected`).

    Minimum size is enforced at 120×40 px as per the tile visual spec.
    """

    def __init__(
        self, component: ConkyComponent, display_name: str, canvas: "Canvas"
    ) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        self.component = component  # live reference — mutated by canvas operations
        self._canvas = canvas  # back-reference for selection callbacks
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

        # Track pointer offset at drag-start so the tile doesn't jump.
        self._drag_offset_x: float = 0.0
        self._drag_offset_y: float = 0.0

        self._setup_drag_source()
        self._setup_click_gesture()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _setup_click_gesture(self) -> None:
        """Attach a Gtk.GestureClick so clicking the tile selects it."""
        gesture = Gtk.GestureClick()
        gesture.set_button(1)  # primary mouse button

        def on_pressed(
            _gesture: Gtk.GestureClick,
            _n_press: int,
            _x: float,
            _y: float,
        ) -> None:
            self._canvas.select_tile(self.component.id)

        gesture.connect("pressed", on_pressed)
        self.add_controller(gesture)

    def _setup_drag_source(self) -> None:
        """Attach a Gtk.DragSource for tile-move operations."""
        drag_source = Gtk.DragSource()
        drag_source.set_actions(Gdk.DragAction.MOVE)

        def on_prepare(
            source: Gtk.DragSource, x: float, y: float
        ) -> Gdk.ContentProvider:
            # Remember where inside the tile the drag started.
            self._drag_offset_x = x
            self._drag_offset_y = y
            value = GObject.Value()
            value.init(GObject.TYPE_STRING)
            value.set_string(_TILE_DRAG_PREFIX + self.component.id)
            return Gdk.ContentProvider.new_for_value(value)

        drag_source.connect("prepare", on_prepare)
        self.add_controller(drag_source)

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

        # Currently selected component id (None = nothing selected).
        self.selected_component_id: str | None = None

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
        # Wire up click-on-blank-area for deselect.
        self._setup_background_click()
        # Wire up keyboard delete for removing the selected component.
        self._setup_key_controller()

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

    def _setup_background_click(self) -> None:
        """Attach a Gtk.GestureClick on the Gtk.Fixed to deselect on blank clicks."""
        gesture = Gtk.GestureClick()
        gesture.set_button(1)

        def on_pressed(
            _gesture: Gtk.GestureClick,
            _n_press: int,
            _x: float,
            _y: float,
        ) -> None:
            self.deselect_all()
            self.selected_component_id = None
            if self.main_window is not None:
                self.main_window.on_selection_changed(None)

        gesture.connect("pressed", on_pressed)
        self.fixed.add_controller(gesture)

    def _setup_key_controller(self) -> None:
        """Attach a Gtk.EventControllerKey to handle the Delete key.

        The canvas must be focusable for key events to reach it; we set
        ``can-focus`` on the :class:`Gtk.Fixed` so clicking a tile (or the
        background) naturally moves focus here.
        """
        self.fixed.set_focusable(True)

        key_ctrl = Gtk.EventControllerKey()

        def on_key_pressed(
            _ctrl: Gtk.EventControllerKey,
            keyval: int,
            _keycode: int,
            _state: Gdk.ModifierType,
        ) -> bool:
            # Gdk.KEY_Delete = 0xffff
            if keyval == Gdk.KEY_Delete:
                self.delete_selected()
                return True  # event consumed
            return False

        key_ctrl.connect("key-pressed", on_key_pressed)
        self.fixed.add_controller(key_ctrl)

    def _setup_drop_target(self) -> None:
        """Attach a Gtk.DropTarget to the Gtk.Fixed for all canvas drops.

        Handles both library → canvas (COPY action, plain type key) and
        tile-move (MOVE action, ``"tile:<id>"`` payload) drops via a single
        controller that accepts both actions.
        """
        drop_target = Gtk.DropTarget.new(
            GObject.TYPE_STRING,
            Gdk.DragAction.COPY | Gdk.DragAction.MOVE,
        )
        drop_target.connect("drop", self._on_canvas_drop)
        self.fixed.add_controller(drop_target)

    def _on_canvas_drop(
        self,
        _target: Gtk.DropTarget,
        value: str,
        x: float,
        y: float,
    ) -> bool:
        """Dispatch canvas drops to the correct handler based on payload prefix."""
        if value.startswith(_TILE_DRAG_PREFIX):
            return self._on_tile_move_drop(value[len(_TILE_DRAG_PREFIX) :], x, y)
        return self._on_library_drop(value, x, y)

    def _on_library_drop(self, type_key: str, x: float, y: float) -> bool:
        """Handle a drop from the component library.

        Creates a new :class:`ConkyComponent` of the dropped type, appends it
        to the document, and places a :class:`CanvasTile` at the drop point.
        Returns True to indicate the drop was accepted.
        """
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
        tile = CanvasTile(component, component_cls.DISPLAY_NAME, self)
        self.add_tile(tile, canvas_x, canvas_y)
        return True

    def _on_tile_move_drop(self, component_id: str, x: float, y: float) -> bool:
        """Handle a tile-move drop — reposition the tile and update the model."""
        tile = self._tile_map.get(component_id)
        if tile is None:
            return False

        # Adjust by the drag-start offset so the tile follows the cursor.
        new_x = max(0, int(x - tile._drag_offset_x))
        new_y = max(0, int(y - tile._drag_offset_y))

        self.move_tile(component_id, new_x, new_y)

        if self.main_window is not None:
            self.main_window.on_document_changed()
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

    def select_tile(self, component_id: str) -> None:
        """Select the tile for *component_id*, deselecting all others.

        Updates :attr:`selected_component_id` and notifies the main window via
        :meth:`~MainWindow.on_selection_changed` so the properties panel can
        refresh.  Grabs keyboard focus on the fixed surface so Delete events
        are delivered to the key controller.

        Also brings the tile to the front of the z-order by removing and
        re-placing it at its stored coordinates — this ensures the selected
        tile is always rendered on top of all others.
        """
        self.deselect_all()
        tile = self._tile_map.get(component_id)
        if tile is not None:
            tile.set_selected(True)
            # Bring to front: remove then re-put at the same position.
            self.fixed.remove(tile)
            self.fixed.put(tile, tile.component.canvas_x, tile.component.canvas_y)
        self.selected_component_id = component_id
        # Grab focus so key events (Delete) reach the EventControllerKey.
        self.fixed.grab_focus()
        if self.main_window is not None:
            self.main_window.on_selection_changed(component_id)

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

    def delete_selected(self) -> None:
        """Delete the currently selected component from the document and canvas.

        Does nothing if no component is selected.
        """
        component_id = self.selected_component_id
        if component_id is None:
            return

        # Remove from document.
        if self.main_window is not None:
            doc = self.main_window.document
            doc.components = [
                c for c in doc.components if c.id != component_id
            ]
            self.main_window.on_document_changed()

        # Remove tile from canvas.
        self.remove_tile(component_id)
        self.selected_component_id = None
        if self.main_window is not None:
            self.main_window.on_selection_changed(None)

    def rebuild_from_document(self, doc: GonkyDocument) -> None:
        """Reconstruct all tiles from a loaded document.

        Clears every existing tile from the canvas, then creates one
        :class:`CanvasTile` per :class:`~gonky.models.component.ConkyComponent`
        in the document at its stored ``canvas_x``/``canvas_y`` position.

        Calling this method also clears the current selection.
        """
        # Clear existing tiles.
        for component_id in list(self._tile_map):
            tile = self._tile_map.pop(component_id)
            self.fixed.remove(tile)
        self.selected_component_id = None

        # Restore placeholder if document has no components.
        if not doc.components:
            self._show_placeholder_if_empty()
            return

        self._hide_placeholder()

        for component in doc.components:
            component_cls = COMPONENT_REGISTRY.get(component.component_type)
            display_name = (
                component_cls.DISPLAY_NAME
                if component_cls is not None
                else component.component_type
            )
            tile = CanvasTile(component, display_name, self)
            self._tile_map[component.id] = tile
            self.fixed.put(tile, component.canvas_x, component.canvas_y)

    def deselect_all(self) -> None:
        """Remove the selected CSS class from every tile."""
        for tile in self._tile_map.values():
            tile.set_selected(False)
