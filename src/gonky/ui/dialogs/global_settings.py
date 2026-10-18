"""Global settings editor dialog."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from typing import Callable

from gonky.components.base import PropertyField
from gonky.models.document import GonkyDocument
from gonky.ui import form_builder


# PropertyField descriptors for every GlobalConkySettings field.
# (GlobalConkySettings is a plain dataclass with no property_schema(),
#  so the field list is defined here.)
_SETTINGS_FIELDS: list[PropertyField] = [
    PropertyField(
        key="alignment",
        label="Alignment",
        field_type="choice",
        default="top_left",
        choices=[
            "top_left", "top_right", "bottom_left", "bottom_right",
            "top_middle", "bottom_middle",
            "middle_left", "middle_right", "middle_middle",
            "none",
        ],
    ),
    PropertyField(key="gap_x", label="Gap X", field_type="int", default=10, min_val=0),
    PropertyField(key="gap_y", label="Gap Y", field_type="int", default=10, min_val=0),
    PropertyField(key="window_width", label="Window Width", field_type="int", default=300, min_val=0),
    PropertyField(key="window_height", label="Window Height", field_type="int", default=0, min_val=0),
    PropertyField(key="own_window", label="Own Window", field_type="bool", default=True),
    PropertyField(
        key="own_window_type",
        label="Window Type",
        field_type="choice",
        default="desktop",
        choices=["desktop", "normal", "dock", "panel", "override"],
    ),
    PropertyField(key="own_window_transparent", label="Transparent", field_type="bool", default=True),
    PropertyField(key="own_window_argb_visual", label="ARGB Visual", field_type="bool", default=True),
    PropertyField(
        key="own_window_colour",
        label="Window Background Color",
        field_type="color",
        default="",
        tooltip="Background color used when transparency is disabled",
    ),
    PropertyField(key="background", label="Background", field_type="bool", default=False),
    PropertyField(key="double_buffer", label="Double Buffer", field_type="bool", default=True),
    PropertyField(key="border_width", label="Border Width", field_type="int", default=0, min_val=0),
    PropertyField(key="default_font", label="Default Font", field_type="font", default="DejaVu Sans Mono"),
    PropertyField(key="default_font_size", label="Font Size", field_type="int", default=10, min_val=1, max_val=144),
    PropertyField(key="default_color", label="Default Color", field_type="color", default="white"),
    PropertyField(key="update_interval", label="Update Interval", field_type="float", default=1.0, min_val=0.1, max_val=60.0),
    PropertyField(key="cpu_avg_samples", label="CPU Avg Samples", field_type="int", default=2, min_val=1, max_val=32),
    PropertyField(key="net_avg_samples", label="Net Avg Samples", field_type="int", default=2, min_val=1, max_val=32),
    PropertyField(key="extra_lua", label="Extra Lua", field_type="text", default="", tooltip="Raw Lua appended to the Conky config file"),
]


class GlobalSettingsDialog(Gtk.Window):
    """Modal window for editing GlobalConkySettings."""

    def __init__(
        self,
        parent: Gtk.Window,
        document: GonkyDocument,
        on_document_changed: Callable[[], None],
    ) -> None:
        super().__init__()
        self.set_title("Global Settings")
        self.set_transient_for(parent)
        self.set_modal(True)
        self.set_default_size(400, 560)
        self.set_resizable(True)

        # -- Scrolled content --------------------------------------------
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.set_vexpand(True)

        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        content.set_margin_start(12)
        content.set_margin_end(12)
        content.set_margin_top(8)
        content.set_margin_bottom(8)
        scroll.set_child(content)

        # Build one row per field
        settings = document.settings
        for field in _SETTINGS_FIELDS:
            current = getattr(settings, field.key, field.default)

            def _make_cb(f: PropertyField) -> Callable:
                def _cb(value) -> None:
                    setattr(settings, f.key, value)
                    on_document_changed()
                return _cb

            row = form_builder.make_field_widget(field, current, _make_cb(field))
            content.append(row)

        # -- Close button ------------------------------------------------
        btn_close = Gtk.Button(label="Close")
        btn_close.set_halign(Gtk.Align.END)
        btn_close.set_margin_top(8)
        btn_close.set_margin_end(12)
        btn_close.set_margin_bottom(8)
        btn_close.connect("clicked", lambda _: self.close())

        # -- Root layout -------------------------------------------------
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        root.append(scroll)
        root.append(btn_close)
        self.set_child(root)

    # ------------------------------------------------------------------
    # Convenience factory
    # ------------------------------------------------------------------

    @staticmethod
    def open(
        parent: Gtk.Window,
        document: GonkyDocument,
        on_document_changed: Callable[[], None],
    ) -> None:
        """Create and present a GlobalSettingsDialog."""
        dlg = GlobalSettingsDialog(parent, document, on_document_changed)
        dlg.present()
