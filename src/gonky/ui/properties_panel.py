"""Properties panel — scrolled container for the component property form."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from typing import Callable

from gonky.models.component import ConkyComponent, COMPONENT_REGISTRY
from gonky.ui import form_builder
from gonky.components.base import PropertyField


class PropertiesPanel(Gtk.ScrolledWindow):
    """Right-hand panel displaying properties for the selected component.

    Sub-Task 4: shows a 'No component selected' placeholder.
    Sub-Task 7: show_component() replaces the placeholder with live fields.
    """

    def __init__(self) -> None:
        super().__init__()
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.set_min_content_width(280)
        self.add_css_class("properties-panel")

        self._content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=0
        )
        self.set_child(self._content_box)

        self._show_placeholder()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _show_placeholder(self) -> None:
        """Render the 'No component selected' empty state."""
        label = Gtk.Label(label="No component selected")
        label.set_vexpand(True)
        label.set_hexpand(True)
        label.set_valign(Gtk.Align.CENTER)
        label.set_halign(Gtk.Align.CENTER)
        label.add_css_class("dim-label")
        self._content_box.append(label)

    def _append_row(self, label_text: str, widget: Gtk.Widget) -> None:
        """Append a labelled row directly (for the two universal fields)."""
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        lbl = Gtk.Label(label=label_text)
        lbl.set_halign(Gtk.Align.START)
        lbl.set_hexpand(False)
        widget.set_hexpand(True)
        row.append(lbl)
        row.append(widget)
        self._content_box.append(row)

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def clear(self) -> None:
        """Remove all children from the content box and restore the placeholder."""
        child = self._content_box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._content_box.remove(child)
            child = next_child
        self._show_placeholder()

    def show_component(
        self,
        component: ConkyComponent,
        on_changed: Callable[[], None],
    ) -> None:
        """Populate the panel with property widgets for *component*.

        Clears any existing content, adds a section heading, the two
        universal rows (label, enabled), then one row per PropertyField
        returned by the component's property_schema().
        """
        # Wipe existing content (without restoring placeholder)
        child = self._content_box.get_first_child()
        while child is not None:
            next_child = child.get_next_sibling()
            self._content_box.remove(child)
            child = next_child

        # -- Section heading ---------------------------------------------
        cls = COMPONENT_REGISTRY.get(component.component_type)
        heading_text = cls.DISPLAY_NAME if cls is not None else component.component_type
        heading = Gtk.Label(label=heading_text)
        heading.set_halign(Gtk.Align.START)
        heading.set_margin_start(8)
        heading.set_margin_top(8)
        heading.set_margin_bottom(4)
        heading.add_css_class("heading")
        self._content_box.append(heading)

        # -- Universal row 1: label ---------------------------------------
        label_entry = Gtk.Entry()
        label_entry.set_text(component.label)
        label_entry.connect(
            "changed",
            lambda w: (setattr(component, "label", w.get_text()), on_changed()),
        )
        self._append_row("Label", label_entry)

        # -- Universal row 2: label color --------------------------------
        def _on_label_color_changed(value: str) -> None:
            component.label_color = value
            on_changed()

        label_color_field = PropertyField(
            key="label_color",
            label="Label Color",
            field_type="color",
            default="",
            tooltip="Color of the label prefix; leave unset to inherit the default color",
        )
        label_color_row = form_builder.make_field_widget(
            label_color_field, component.label_color, _on_label_color_changed
        )
        self._content_box.append(label_color_row)

        # -- Universal row 3: enabled ------------------------------------
        enabled_switch = Gtk.Switch()
        enabled_switch.set_active(component.enabled)
        enabled_switch.set_halign(Gtk.Align.END)
        enabled_switch.connect(
            "notify::active",
            lambda w, _: (setattr(component, "enabled", w.get_active()), on_changed()),
        )
        self._append_row("Enabled", enabled_switch)

        # -- Universal row 4: no_newline ---------------------------------
        no_newline_switch = Gtk.Switch()
        no_newline_switch.set_active(component.no_newline)
        no_newline_switch.set_halign(Gtk.Align.END)
        no_newline_switch.connect(
            "notify::active",
            lambda w, _: (setattr(component, "no_newline", w.get_active()), on_changed()),
        )
        self._append_row("No newline", no_newline_switch)

        # -- Per-schema fields -------------------------------------------
        if cls is None:
            return

        for field in cls.property_schema():
            current = component.properties.get(field.key, field.default)

            def _make_callback(f: PropertyField) -> Callable:
                def _cb(value) -> None:
                    component.properties[f.key] = value
                    on_changed()
                return _cb

            row = form_builder.make_field_widget(field, current, _make_callback(field))
            self._content_box.append(row)
