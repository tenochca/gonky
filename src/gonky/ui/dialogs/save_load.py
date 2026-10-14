"""Save/load/export file dialogs — async Gtk.FileDialog wrappers."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio  # noqa: E402


def _gonky_filter() -> Gtk.FileFilter:
    """Return a file filter that matches `.gonky` project files."""
    f = Gtk.FileFilter()
    f.set_name("Gonky project (*.gonky)")
    f.add_pattern("*.gonky")
    return f


def _conf_filter() -> Gtk.FileFilter:
    """Return a file filter that matches `.conf` config files."""
    f = Gtk.FileFilter()
    f.set_name("Conky config (*.conf)")
    f.add_pattern("*.conf")
    return f


def _all_filter() -> Gtk.FileFilter:
    """Return a catch-all file filter."""
    f = Gtk.FileFilter()
    f.set_name("All files")
    f.add_pattern("*")
    return f


def open_project_dialog(
    parent: Gtk.Window,
    on_path: Callable[[Path], None],
) -> None:
    """Show an async Open dialog filtered to `.gonky` files.

    Calls *on_path* with the chosen ``Path`` if the user confirms.
    """
    dialog = Gtk.FileDialog()
    dialog.set_title("Open Project")

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(_gonky_filter())
    filters.append(_all_filter())
    dialog.set_filters(filters)
    dialog.set_default_filter(_gonky_filter())

    def _cb(dlg: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            gfile = dlg.open_finish(result)
        except Exception:  # user cancelled or error
            return
        if gfile is not None:
            on_path(Path(gfile.get_path()))

    dialog.open(parent, None, _cb)


def save_project_dialog(
    parent: Gtk.Window,
    suggested_name: str,
    on_path: Callable[[Path], None],
) -> None:
    """Show an async Save dialog filtered to `.gonky` files.

    Calls *on_path* with the chosen ``Path`` if the user confirms.
    """
    dialog = Gtk.FileDialog()
    dialog.set_title("Save Project")
    dialog.set_initial_name(
        suggested_name if suggested_name.endswith(".gonky") else f"{suggested_name}.gonky"
    )

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(_gonky_filter())
    filters.append(_all_filter())
    dialog.set_filters(filters)
    dialog.set_default_filter(_gonky_filter())

    def _cb(dlg: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            gfile = dlg.save_finish(result)
        except Exception:  # user cancelled or error
            return
        if gfile is not None:
            on_path(Path(gfile.get_path()))

    dialog.save(parent, None, _cb)


def export_config_dialog(
    parent: Gtk.Window,
    default_path: Path,
    on_path: Callable[[Path], None],
) -> None:
    """Show an async Save dialog for exporting a Conky `.conf` file.

    Calls *on_path* with the chosen ``Path`` if the user confirms.
    If the chosen file already exists, shows a confirmation dialog first.
    """
    dialog = Gtk.FileDialog()
    dialog.set_title("Export Conky Config")
    dialog.set_initial_name(default_path.name)
    dialog.set_initial_folder(Gio.File.new_for_path(str(default_path.parent)))

    filters = Gio.ListStore.new(Gtk.FileFilter)
    filters.append(_conf_filter())
    filters.append(_all_filter())
    dialog.set_filters(filters)
    dialog.set_default_filter(_conf_filter())

    def _confirm_overwrite(path: Path) -> None:
        """If the file exists ask for confirmation before calling on_path."""
        if not path.exists():
            on_path(path)
            return

        confirm = Gtk.MessageDialog(
            transient_for=parent,
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Overwrite {path.name}?",
            secondary_text=str(path),
        )
        confirm.connect(
            "response",
            lambda dlg, resp: (
                on_path(path) if resp == Gtk.ResponseType.YES else None,
                dlg.destroy(),
            ),
        )
        confirm.present()

    def _cb(dlg: Gtk.FileDialog, result: Gio.AsyncResult) -> None:
        try:
            gfile = dlg.save_finish(result)
        except Exception:  # user cancelled or error
            return
        if gfile is not None:
            _confirm_overwrite(Path(gfile.get_path()))

    dialog.save(parent, None, _cb)
