"""Form builder — widget factory for PropertyField descriptors."""

import gi
gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gtk, Gdk  # noqa: E402

from typing import Any, Callable
from gonky.components.base import PropertyField


def make_field_widget(
    field: PropertyField,
    current_value: Any,
    on_change: Callable[[Any], None],
) -> Gtk.Widget:
    """Create a labelled row widget for a single PropertyField.

    Returns a horizontal Gtk.Box containing a left-aligned label and the
    appropriate input widget for *field.field_type*, pre-filled with
    *current_value*.  Any user change calls *on_change* with the new value.
    """
    widget = _build_input(field, current_value, on_change)
    if field.tooltip:
        widget.set_tooltip_text(field.tooltip)
    return _wrap_row(field.label, widget)

def _build_input(
    field: PropertyField,
    current_value: Any,
    on_change: Callable[[Any], None],
) -> Gtk.Widget:
    match field.field_type:
        case "text":
            entry = Gtk.Entry()
            entry.set_text(str(current_value) if current_value is not None else "")
            entry.set_hexpand(True)
            entry.connect("changed", lambda w: on_change(w.get_text()))
            return entry

        case "int":
            adj = Gtk.Adjustment(
                value=float(current_value) if current_value is not None else 0.0,
                lower=float(field.min_val) if field.min_val is not None else 0.0,
                upper=float(field.max_val) if field.max_val is not None else 9999.0,
                step_increment=1.0,
                page_increment=10.0,
                page_size=0.0,
            )
            spin = Gtk.SpinButton(adjustment=adj, digits=0)
            spin.set_hexpand(True)
            spin.connect("value-changed", lambda w: on_change(int(w.get_value())))
            return spin

        case "float":
            adj = Gtk.Adjustment(
                value=float(current_value) if current_value is not None else 0.0,
                lower=float(field.min_val) if field.min_val is not None else 0.0,
                upper=float(field.max_val) if field.max_val is not None else 9999.0,
                step_increment=1.0,
                page_increment=10.0,
                page_size=0.0,
            )
            spin = Gtk.SpinButton(adjustment=adj, digits=2)
            spin.set_hexpand(True)
            spin.connect("value-changed", lambda w: on_change(w.get_value()))
            return spin

        case "bool":
            switch = Gtk.Switch()
            switch.set_active(bool(current_value))
            switch.set_halign(Gtk.Align.END)
            switch.connect("notify::active", lambda w, _: on_change(w.get_active()))
            return switch

        case "color":
            btn = Gtk.ColorButton()
            btn.set_hexpand(True)
            rgba = Gdk.RGBA()
            if current_value and current_value != "":
                rgba.parse(current_value)
            else:
                rgba.parse("white")
            btn.set_rgba(rgba)

            def _on_color_set(w: Gtk.ColorButton) -> None:
                c = w.get_rgba()
                hex_color = "#{:02x}{:02x}{:02x}".format(
                    int(c.red * 255),
                    int(c.green * 255),
                    int(c.blue * 255),
                )
                on_change(hex_color)

            btn.connect("color-set", _on_color_set)
            return btn

        case "choice":
            choices = field.choices or []
            string_list = Gtk.StringList.new(choices)
            dropdown = Gtk.DropDown(model=string_list)
            dropdown.set_hexpand(True)
            try:
                idx = choices.index(current_value)
            except ValueError:
                idx = 0
            dropdown.set_selected(idx)
            dropdown.connect(
                "notify::selected",
                lambda w, _: on_change(choices[w.get_selected()]) if choices else None,
            )
            return dropdown

        case "font":
            font_btn = Gtk.FontButton()
            font_btn.set_hexpand(True)
            if current_value:
                font_btn.set_font(str(current_value))
            font_btn.connect("font-set", lambda w: on_change(w.get_font()))
            return font_btn

        case _: # fallback
            return Gtk.Label(label=str(current_value))


def _wrap_row(label_text: str, widget: Gtk.Widget) -> Gtk.Box:
    """Return a horizontal box with a left-aligned label and the input widget."""
    row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
    label = Gtk.Label(label=label_text)
    label.set_halign(Gtk.Align.START)
    label.set_hexpand(False)
    row.append(label)
    row.append(widget)
    return row
