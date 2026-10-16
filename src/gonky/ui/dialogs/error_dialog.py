"""Scrollable validation error/warning dialog."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from gonky.logic.validator import ValidationError


def show_validation_errors(
    parent: Gtk.Window,
    errors: list[ValidationError],
    *,
    allow_proceed: bool = False,
) -> bool:
    """Display a scrollable list of *errors* in a modal dialog.

    Parameters
    ----------
    parent:
        Transient parent window.
    errors:
        List of :class:`~gonky.logic.validator.ValidationError` instances to
        display.  Must not be empty.
    allow_proceed:
        When *True* a "Proceed Anyway" button is added alongside "Close" — used
        for warning-only dialogs where the user may still choose to continue.

    Returns
    -------
    bool
        ``True`` if the user chose to proceed (only possible when
        *allow_proceed* is ``True``), ``False`` otherwise.
    """
    has_errors = any(e.severity == "error" for e in errors)
    has_warnings = any(e.severity == "warning" for e in errors)

    if has_errors:
        title = "Validation Errors"
        heading = "The following errors must be fixed before proceeding:"
    elif has_warnings:
        title = "Validation Warnings"
        heading = "The following warnings were found:"
    else:
        title = "Validation"
        heading = "Validation findings:"

    dialog = Gtk.Dialog()
    dialog.set_title(title)
    dialog.set_transient_for(parent)
    dialog.set_modal(True)
    dialog.set_default_size(520, 380)

    # Buttons
    dialog.add_button("Close", Gtk.ResponseType.CLOSE)
    if allow_proceed:
        dialog.add_button("Proceed Anyway", Gtk.ResponseType.OK)

    # Content area
    content = dialog.get_content_area()
    content.set_spacing(8)
    content.set_margin_top(12)
    content.set_margin_bottom(12)
    content.set_margin_start(16)
    content.set_margin_end(16)

    # Heading label
    heading_label = Gtk.Label(label=heading)
    heading_label.set_xalign(0.0)
    heading_label.set_wrap(True)
    content.append(heading_label)

    # Scrollable list of errors
    scroll = Gtk.ScrolledWindow()
    scroll.set_vexpand(True)
    scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

    list_box = Gtk.ListBox()
    list_box.set_selection_mode(Gtk.SelectionMode.NONE)
    list_box.add_css_class("boxed-list")

    for err in errors:
        row = _make_error_row(err)
        list_box.append(row)

    scroll.set_child(list_box)
    content.append(scroll)

    # Run
    proceeded = False

    def _on_response(dlg: Gtk.Dialog, response: int) -> None:
        nonlocal proceeded
        if response == Gtk.ResponseType.OK:
            proceeded = True
        dlg.close()

    dialog.connect("response", _on_response)
    dialog.present()

    # Use a local main loop so this call blocks until the dialog closes.
    loop = _modal_loop(dialog)
    loop.run()

    return proceeded


def _make_error_row(error: ValidationError) -> Gtk.ListBoxRow:
    """Build a single row widget for one :class:`ValidationError`."""
    row = Gtk.ListBoxRow()
    row.set_activatable(False)

    hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    hbox.set_margin_top(6)
    hbox.set_margin_bottom(6)
    hbox.set_margin_start(8)
    hbox.set_margin_end(8)

    # Severity icon
    if error.severity == "error":
        icon_name = "dialog-error-symbolic"
    else:
        icon_name = "dialog-warning-symbolic"

    icon = Gtk.Image.new_from_icon_name(icon_name)
    icon.set_pixel_size(16)
    hbox.append(icon)

    # Message text
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)

    msg_label = Gtk.Label(label=error.message)
    msg_label.set_xalign(0.0)
    msg_label.set_wrap(True)
    msg_label.set_hexpand(True)
    vbox.append(msg_label)

    # Field / component context shown as muted subtitle
    context_parts: list[str] = []
    if error.component_id is not None:
        context_parts.append(f"component: {error.component_id}")
    if error.field:
        context_parts.append(f"field: {error.field}")

    if context_parts:
        ctx_label = Gtk.Label(label=" · ".join(context_parts))
        ctx_label.set_xalign(0.0)
        ctx_label.add_css_class("dim-label")
        ctx_label.set_wrap(True)
        ctx_label.set_hexpand(True)
        vbox.append(ctx_label)

    hbox.append(vbox)
    row.set_child(hbox)
    return row


def _modal_loop(dialog: Gtk.Dialog):
    """Return a GLib main loop that stops when *dialog* is destroyed."""
    from gi.repository import GLib  # local import to avoid top-level GLib dep

    loop = GLib.MainLoop()
    dialog.connect("destroy", lambda *_: loop.quit())
    return loop

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
