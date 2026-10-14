"""New project dialog — prompts for a project name and creates a blank document."""

from __future__ import annotations

from typing import Callable

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from gonky.models.document import GonkyDocument


def show_new_project_dialog(
    parent: Gtk.Window,
    on_created: Callable[[GonkyDocument], None],
) -> None:
    """Show a modal dialog asking for a project name.

    Calls *on_created* with a blank ``GonkyDocument`` if the user confirms.
    """
    dialog = Gtk.Dialog(title="New Project", transient_for=parent, modal=True)
    dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
    dialog.add_button("Create", Gtk.ResponseType.OK)
    dialog.set_default_response(Gtk.ResponseType.OK)

    content = dialog.get_content_area()
    content.set_spacing(8)
    content.set_margin_top(16)
    content.set_margin_bottom(16)
    content.set_margin_start(16)
    content.set_margin_end(16)

    label = Gtk.Label(label="Project name:")
    label.set_halign(Gtk.Align.START)
    content.append(label)

    entry = Gtk.Entry()
    entry.set_text("Untitled")
    entry.set_activates_default(True)
    entry.set_hexpand(True)
    content.append(entry)

    def _on_response(dlg: Gtk.Dialog, response: int) -> None:
        dlg.destroy()
        if response == Gtk.ResponseType.OK:
            name = entry.get_text().strip() or "Untitled"
            doc = GonkyDocument(project_name=name)
            on_created(doc)

    dialog.connect("response", _on_response)
    dialog.present()
