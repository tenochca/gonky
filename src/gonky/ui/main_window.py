"""MainWindow — primary application window with full panel layout."""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from gonky.logic import file_manager
from gonky.logic.validator import Validator
from gonky.models.document import GonkyDocument, SchemaVersionError
from gonky.ui.canvas import Canvas
from gonky.ui.component_library import ComponentLibrary
from gonky.ui.dialogs.error_dialog import show_validation_errors
from gonky.ui.dialogs.global_settings import GlobalSettingsDialog
from gonky.ui.dialogs.new_project import show_new_project_dialog
from gonky.ui.dialogs.save_load import (
    export_config_dialog,
    open_project_dialog,
    save_project_dialog,
)
from gonky.ui.properties_panel import PropertiesPanel
from gonky.ui.statusbar import StatusBar
from gonky.ui.toolbar import ToolBar

# App title shown in the header bar.
_APP_TITLE = "Gonky"


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

        # Path of the last saved/opened file; None until first save.
        self._project_path: str | None = None

        # Dirty flag — True when there are unsaved changes.
        self._is_dirty: bool = False

        # -- Toolbar (HeaderBar) -----------------------------------------
        self.toolbar = ToolBar()
        self.set_titlebar(self.toolbar)
        self._update_title()

        # Wire validation-guarded Export and Apply actions
        self.toolbar.btn_export.connect("clicked", self._on_export_clicked)
        self.toolbar.btn_apply.connect("clicked", self._on_apply_clicked)

        # -- Panels -------------------------------------------------------
        self.component_library = ComponentLibrary()
        self.canvas = Canvas()
        self.canvas.main_window = self  # back-reference for drop/delete handlers
        self.properties_panel = PropertiesPanel()
        self.statusbar = StatusBar()

        # Wire canvas selection → PropertiesPanel
        self.canvas.on_component_selected = (
            lambda c: self.properties_panel.show_component(c, self.on_document_changed)
        )
        self.canvas.on_component_deselected = self.properties_panel.clear

        # Wire toolbar buttons
        self.toolbar.btn_new.connect("clicked", self._on_new)
        self.toolbar.btn_open.connect("clicked", self._on_open)
        self.toolbar.btn_save.connect("clicked", self._on_save)
        self.toolbar.btn_export.connect("clicked", self._on_export)
        self.toolbar.btn_settings.connect(
            "clicked",
            lambda _: GlobalSettingsDialog.open(self, self.document, self.on_document_changed),
        )

        # Close guard — intercept the window-close request.
        self.connect("close-request", self._on_close_request)

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
    # Document lifecycle
    # ------------------------------------------------------------------

    def on_document_changed(self) -> None:
        """Called by any panel after mutating self.document.

        Sets the dirty flag and updates the window title to show an asterisk.
        """
        self._is_dirty = True
        self._update_title()

    def _load_document(self, doc: GonkyDocument, path: str | None = None) -> None:
        """Replace the active document, reset dirty state, rebuild the canvas."""
        self.document = doc
        self._project_path = path
        self._is_dirty = False
        self._update_title()
        self.canvas.rebuild_from_document(doc)
        self.properties_panel.clear()

    def _update_title(self) -> None:
        """Refresh the header-bar title to reflect the project name and dirty state."""
        name = self.document.project_name if hasattr(self, "document") else "Untitled"
        dirty_marker = "*" if self._is_dirty else ""
        self.toolbar.set_title_widget(
            Gtk.Label(
                label=(f"{dirty_marker}{name} — {_APP_TITLE}")
            )
        )

    def _guard_unsaved(self, proceed: "Callable[[], None]") -> None:  # type: ignore[name-defined]
        """If there are unsaved changes, prompt the user before calling *proceed*.

        If the document is clean, *proceed* is called immediately.
        """
        if not self._is_dirty:
            proceed()
            return

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            text="Save changes?",
            secondary_text=(
                f"Project \"{self.document.project_name}\" has unsaved changes."
            ),
        )
        dialog.add_button("Discard", Gtk.ResponseType.NO)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        save_btn = dialog.add_button("Save", Gtk.ResponseType.YES)
        save_btn.add_css_class("suggested-action")

        def _on_response(dlg: Gtk.MessageDialog, response: int) -> None:
            dlg.destroy()
            if response == Gtk.ResponseType.YES:
                if self._project_path:
                    self._save_to_path(self._project_path)
                    if not self._is_dirty:
                        proceed()
                else:
                    save_project_dialog(
                        self,
                        self.document.project_name,
                        lambda p: (self._save_to_path(str(p)), proceed()),
                    )
            elif response == Gtk.ResponseType.NO:
                proceed()
            # CANCEL: do nothing.

        dialog.connect("response", _on_response)
        dialog.present()

    # ------------------------------------------------------------------
    # Toolbar handlers
    # ------------------------------------------------------------------

    def _on_new(self, _btn: Gtk.Button) -> None:
        """Handle New — guard against unsaved changes, then prompt for a name."""
        self._guard_unsaved(lambda: show_new_project_dialog(self, self._load_document))

    def _on_open(self, _btn: Gtk.Button) -> None:
        """Handle Open — guard against unsaved changes, then show open dialog."""
        def _do_open() -> None:
            open_project_dialog(self, self._open_path)

        self._guard_unsaved(_do_open)

    def _open_path(self, path: "Path") -> None:  # type: ignore[name-defined]
        """Load a project from *path*, showing an error dialog on failure."""
        try:
            doc = file_manager.load_project(path)
        except SchemaVersionError as exc:
            self._show_error("Cannot open project", str(exc))
            return
        except Exception as exc:
            self._show_error("Error opening project", str(exc))
            return
        self._load_document(doc, str(path))

    def _on_save(self, _btn: Gtk.Button) -> None:
        """Handle Save — save in-place if path known, otherwise prompt."""
        if self._project_path:
            self._save_to_path(self._project_path)
        else:
            save_project_dialog(
                self,
                self.document.project_name,
                lambda p: self._save_to_path(str(p)),
            )

    def _save_to_path(self, path: str) -> None:
        """Write the document to *path* and clear the dirty flag."""
        from pathlib import Path

        try:
            file_manager.save_project(self.document, Path(path))
        except Exception as exc:
            self._show_error("Error saving project", str(exc))
            return
        self._project_path = str(Path(path).with_suffix(".gonky"))
        self._is_dirty = False
        self._update_title()

    def _on_export(self, _btn: Gtk.Button) -> None:
        """Handle Export — show export dialog pre-filled with default path."""
        export_config_dialog(
            self,
            file_manager.get_default_export_path(),
            self._export_to_path,
        )

    def _export_to_path(self, path: "Path") -> None:  # type: ignore[name-defined]
        """Write a Conky config to *path*, showing an error dialog on failure."""
        try:
            file_manager.export_config(self.document, path)
        except Exception as exc:
            self._show_error("Error exporting config", str(exc))

    # ------------------------------------------------------------------
    # Close guard
    # ------------------------------------------------------------------

    def _on_close_request(self, _win: Gtk.Window) -> bool:
        """Intercept window close; prompt to save if there are unsaved changes.

        Returns True to suppress the default close (i.e. keep the window open)
        when a dialog is shown so the user can choose.  Returns False to allow
        the window to close immediately when there are no unsaved changes.
        """
        if not self._is_dirty:
            return False  # allow close

        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            text="Save changes before closing?",
            secondary_text=(
                f"Project \"{self.document.project_name}\" has unsaved changes."
            ),
        )
        dialog.add_button("Discard", Gtk.ResponseType.NO)
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        save_btn = dialog.add_button("Save", Gtk.ResponseType.YES)
        save_btn.add_css_class("suggested-action")

        def _on_response(dlg: Gtk.MessageDialog, response: int) -> None:
            dlg.destroy()
            if response == Gtk.ResponseType.YES:
                # Save, then close if successful.
                if self._project_path:
                    self._save_to_path(self._project_path)
                    if not self._is_dirty:
                        self.destroy()
                else:
                    save_project_dialog(
                        self,
                        self.document.project_name,
                        lambda p: (self._save_to_path(str(p)), self.destroy()),
                    )
            elif response == Gtk.ResponseType.NO:
                # Discard — force close without saving.
                self._is_dirty = False
                self.destroy()
            # CANCEL: do nothing, window stays open.

        dialog.connect("response", _on_response)
        dialog.present()
        return True  # suppress immediate close

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _show_error(self, title: str, message: str) -> None:
        """Display a simple error message dialog."""
        dlg = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title,
            secondary_text=message,
        )
        dlg.connect("response", lambda d, _: d.destroy())
        dlg.present()

    # ------------------------------------------------------------------
    # Validation-guarded Export / Apply handlers (Sub-Task 10)
    # ------------------------------------------------------------------

    def _run_validation_guard(self) -> bool:
        """Run Validator against self.document.

        Returns True if it is safe to proceed (no errors).  Errors are shown
        in a blocking dialog; warnings also trigger a dialog but the user may
        choose to proceed.
        """
        validator = Validator()
        findings = validator.validate(self.document)

        if not findings:
            return True

        has_errors = any(f.severity == "error" for f in findings)

        if has_errors:
            # Blocking — user must fix errors first.
            show_validation_errors(self, findings, allow_proceed=False)
            return False

        # Warnings only — user may proceed.
        return show_validation_errors(self, findings, allow_proceed=True)

    def _on_export_clicked(self, _btn: Gtk.Button) -> None:
        """Validate the document before running the export flow."""
        if not self._run_validation_guard():
            return
        # Export logic is implemented in Sub-Task 9; placeholder for now.

    def _on_apply_clicked(self, _btn: Gtk.Button) -> None:
        """Validate the document before applying the config to Conky."""
        if not self._run_validation_guard():
            return
        # Apply logic is implemented in Sub-Task 9; placeholder for now.

    def on_selection_changed(self, component_id: str | None) -> None:
        """Called by the canvas when the selected component changes.

        *component_id* is the id of the newly selected component, or None when
        the selection is cleared.

        Sub-Task 5: stores the id for use by Sub-Task 7 (properties panel).
        Sub-Task 7: will call self.properties_panel.load_component(component).
        """
        self.selected_component_id: str | None = component_id
