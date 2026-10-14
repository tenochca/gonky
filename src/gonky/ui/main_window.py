"""MainWindow — primary application window with full panel layout."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from gonky.models.document import GonkyDocument
from gonky.ui.canvas import Canvas
from gonky.ui.component_library import ComponentLibrary
from gonky.ui.properties_panel import PropertiesPanel
from gonky.ui.statusbar import StatusBar
from gonky.ui.toolbar import ToolBar


class MainWindow(Gtk.ApplicationWindow):
    """Primary application window.

    Assembles the full panel layout:
        HeaderBar (toolbar) at the top via set_titlebar()
        Gtk.Box (vertical) as root content:
            Gtk.Paned (horizontal) — library | [canvas + properties]
                Gtk.Paned (horizontal) — canvas | properties
            StatusBar at the bottom

    All panels hold a reference to this window so they can read/write
    self.document and call self.on_document_changed() in later sub-tasks.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_default_size(1280, 800)

        # Active document — panels read and mutate this directly.
        self.document: GonkyDocument = GonkyDocument()

        # -- Toolbar (HeaderBar) -----------------------------------------
        self.toolbar = ToolBar()
        self.set_titlebar(self.toolbar)

        # -- Panels -------------------------------------------------------
        self.component_library = ComponentLibrary()
        self.canvas = Canvas()
        self.canvas.main_window = self  # back-reference for drop/delete handlers
        self.properties_panel = PropertiesPanel()
        self.statusbar = StatusBar()

        # -- Layout: inner pane — canvas (flex) | properties (fixed 280px) -
        inner_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        inner_paned.set_start_child(self.canvas)
        inner_paned.set_end_child(self.properties_panel)
        inner_paned.set_resize_start_child(True)
        inner_paned.set_resize_end_child(False)
        inner_paned.set_shrink_start_child(False)
        inner_paned.set_shrink_end_child(False)

        # -- Layout: outer pane — library (fixed 200px) | inner pane ------
        outer_paned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        outer_paned.set_start_child(self.component_library)
        outer_paned.set_end_child(inner_paned)
        outer_paned.set_position(200)
        outer_paned.set_resize_start_child(False)
        outer_paned.set_resize_end_child(True)
        outer_paned.set_shrink_start_child(False)
        outer_paned.set_shrink_end_child(False)

        # -- Root box: paned area + status bar ----------------------------
        root_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root_box.append(outer_paned)
        root_box.append(self.statusbar)
        self.set_child(root_box)

    # ------------------------------------------------------------------
    # Document lifecycle (wired to business logic in later sub-tasks)
    # ------------------------------------------------------------------

    def on_document_changed(self) -> None:
        """Called by any panel after mutating self.document.

        Sub-Task 4: stub — does nothing yet.
        Sub-Tasks 5–9: will set dirty flag, update title, debounce preview.
        """

    def on_selection_changed(self, component_id: str | None) -> None:
        """Called by the canvas when the selected component changes.

        *component_id* is the id of the newly selected component, or None when
        the selection is cleared.

        Sub-Task 5: stores the id for use by Sub-Task 7 (properties panel).
        Sub-Task 7: will call self.properties_panel.load_component(component).
        """
        self.selected_component_id: str | None = component_id
