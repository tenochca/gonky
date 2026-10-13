"""Scrollable validation error dialog."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


def show_error_dialog(parent: Gtk.Window, errors: list) -> None:
    """Display a modal dialog listing *errors*.

    Each error is expected to have a ``message`` attribute and optionally
    ``component_id`` and ``component_label`` attributes (matching the
    ValidationError shape from logic/validator.py).

    Uses a Gtk.ScrolledWindow wrapping a Gtk.ListBox so the dialog never
    overflows regardless of how many errors are present.
    """
    dlg = Gtk.Window()
    dlg.set_title("Validation Errors")
    dlg.set_transient_for(parent)
    dlg.set_modal(True)
    dlg.set_default_size(420, 320)
    dlg.set_resizable(True)

    # -- Scrolled list of errors -----------------------------------------
    scroll = Gtk.ScrolledWindow()
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
    scroll.set_vexpand(True)

    list_box = Gtk.ListBox()
    list_box.set_selection_mode(Gtk.SelectionMode.NONE)
    list_box.add_css_class("boxed-list")
    scroll.set_child(list_box)

    for error in errors:
        message = getattr(error, "message", str(error))
        component_id = getattr(error, "component_id", None)
        component_label = getattr(error, "component_label", None)

        # Build display text: prepend component identifier if available.
        if component_label:
            text = f"[{component_label}] {message}"
        elif component_id:
            text = f"[{component_id}] {message}"
        else:
            text = message

        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        label = Gtk.Label(label=text)
        label.set_halign(Gtk.Align.START)
        label.set_wrap(True)
        label.set_margin_start(8)
        label.set_margin_end(8)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        row.set_child(label)
        list_box.append(row)

    if not errors:
        row = Gtk.ListBoxRow()
        row.set_activatable(False)
        label = Gtk.Label(label="No errors found.")
        label.set_halign(Gtk.Align.CENTER)
        label.set_margin_top(12)
        label.set_margin_bottom(12)
        row.set_child(label)
        list_box.append(row)

    # -- Close button ----------------------------------------------------
    btn_close = Gtk.Button(label="Close")
    btn_close.set_halign(Gtk.Align.END)
    btn_close.set_margin_top(8)
    btn_close.set_margin_end(12)
    btn_close.set_margin_bottom(8)
    btn_close.connect("clicked", lambda _: dlg.close())

    # -- Root layout -----------------------------------------------------
    root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
    root.set_margin_start(8)
    root.set_margin_end(8)
    root.set_margin_top(8)
    root.append(scroll)
    root.append(btn_close)
    dlg.set_child(root)

    dlg.present()
