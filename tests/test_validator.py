"""Tests for the Validator and per-field validator functions (Sub-Task 10)."""

import pytest

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

from gonky.logic.validator import (
    ValidationError,
    Validator,
    validate_color,
    validate_command,
    validate_font,
    validate_interval,
    validate_mount_point,
    validate_network_interface,
)
from gonky.models.component import ConkyComponent
from gonky.models.document import GonkyDocument
from gonky.models.settings import GlobalConkySettings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_component(
    component_type: str,
    *,
    enabled: bool = True,
    properties: dict | None = None,
) -> ConkyComponent:
    return ConkyComponent(
        component_type=component_type,
        enabled=enabled,
        properties=properties or {},
    )


# ---------------------------------------------------------------------------
# ValidationError dataclass
# ---------------------------------------------------------------------------


class TestValidationError:
    def test_fields_stored(self):
        e = ValidationError(
            field="gap_x",
            component_id="abc",
            message="must be >= 0",
            severity="error",
        )
        assert e.field == "gap_x"
        assert e.component_id == "abc"
        assert e.message == "must be >= 0"
        assert e.severity == "error"

    def test_component_id_can_be_none(self):
        e = ValidationError(field="gap_x", component_id=None, message="x", severity="error")
        assert e.component_id is None

    def test_severity_warning(self):
        e = ValidationError(field="f", component_id=None, message="m", severity="warning")
        assert e.severity == "warning"


# ---------------------------------------------------------------------------
# validate_color
# ---------------------------------------------------------------------------


class TestValidateColor:
    def test_empty_string_is_valid(self):
        # empty = "inherit" sentinel
        assert validate_color("") is True

    def test_three_digit_hex(self):
        assert validate_color("#abc") is True
        assert validate_color("#ABC") is True
        assert validate_color("#000") is True
        assert validate_color("#fff") is True

    def test_six_digit_hex(self):
        assert validate_color("#aabbcc") is True
        assert validate_color("#AABBCC") is True
        assert validate_color("#123456") is True

    def test_eight_digit_hex(self):
        # RRGGBBAA — accepted by the permissive pattern
        assert validate_color("#aabbccdd") is True

    def test_0x_prefix_six_digits(self):
        assert validate_color("0x123456") is True
        assert validate_color("0xFFFFFF") is True
        assert validate_color("0xaabbcc") is True

    def test_named_colour_alphabetic(self):
        assert validate_color("white") is True
        assert validate_color("red") is True
        assert validate_color("DarkSlateGray") is True

    def test_invalid_hex_bad_digits(self):
        assert validate_color("#ZZZZZZ") is False
        assert validate_color("#GGG") is False

    def test_invalid_contains_digits_mixed_with_alpha(self):
        # "not valid 123" — space makes it invalid
        assert validate_color("not valid 123") is False

    def test_invalid_space_in_string(self):
        assert validate_color("dark blue") is False

    def test_invalid_hash_wrong_length(self):
        # 2 chars after # — not 3, 6, or 8
        assert validate_color("#ab") is False

    def test_invalid_0x_five_digits(self):
        assert validate_color("0x12345") is False


# ---------------------------------------------------------------------------
# validate_interval
# ---------------------------------------------------------------------------


class TestValidateInterval:
    def test_minimum_boundary(self):
        assert validate_interval(0.1) is True

    def test_above_minimum(self):
        assert validate_interval(1.0) is True
        assert validate_interval(60.0) is True
        assert validate_interval(0.5) is True

    def test_below_minimum(self):
        assert validate_interval(0.09) is False
        assert validate_interval(0.0) is False
        assert validate_interval(-1.0) is False


# ---------------------------------------------------------------------------
# validate_font
# ---------------------------------------------------------------------------


class TestValidateFont:
    def test_non_empty_string_is_valid(self):
        assert validate_font("DejaVu Sans Mono") is True
        assert validate_font("Noto Sans") is True
        assert validate_font("A") is True

    def test_empty_string_invalid(self):
        assert validate_font("") is False

    def test_whitespace_only_invalid(self):
        assert validate_font("   ") is False


# ---------------------------------------------------------------------------
# validate_mount_point
# ---------------------------------------------------------------------------


class TestValidateMountPoint:
    def test_root_valid(self):
        assert validate_mount_point("/") is True

    def test_absolute_path_valid(self):
        assert validate_mount_point("/home") is True
        assert validate_mount_point("/var/log") is True

    def test_relative_path_invalid(self):
        assert validate_mount_point("home") is False
        assert validate_mount_point("./mnt") is False

    def test_empty_string_invalid(self):
        assert validate_mount_point("") is False


# ---------------------------------------------------------------------------
# validate_network_interface
# ---------------------------------------------------------------------------


class TestValidateNetworkInterface:
    def test_common_names_valid(self):
        assert validate_network_interface("eth0") is True
        assert validate_network_interface("wlan0") is True
        assert validate_network_interface("lo") is True

    def test_empty_string_invalid(self):
        assert validate_network_interface("") is False

    def test_contains_space_invalid(self):
        assert validate_network_interface("eth 0") is False
        assert validate_network_interface(" eth0") is False
        assert validate_network_interface("eth0 ") is False

    def test_contains_tab_invalid(self):
        assert validate_network_interface("eth\t0") is False


# ---------------------------------------------------------------------------
# validate_command
# ---------------------------------------------------------------------------


class TestValidateCommand:
    def test_non_empty_command_valid(self):
        assert validate_command("echo hello") is True
        assert validate_command("ls -la /tmp") is True
        assert validate_command("true") is True

    def test_empty_string_invalid(self):
        assert validate_command("") is False

    def test_whitespace_only_invalid(self):
        assert validate_command("   ") is False


# ---------------------------------------------------------------------------
# Validator — clean document produces no findings
# ---------------------------------------------------------------------------


class TestValidatorCleanDocument:
    def setup_method(self):
        self.v = Validator()

    def test_default_document_is_clean(self):
        doc = GonkyDocument()
        assert self.v.validate(doc) == []

    def test_document_with_valid_components_is_clean(self):
        doc = GonkyDocument(components=[
            make_component("cpu_usage"),
            make_component("ram_usage"),
            make_component("disk_usage"),
        ])
        assert self.v.validate(doc) == []

    def test_disabled_components_are_skipped(self):
        # A disabled component with an invalid mount point should not trigger errors.
        doc = GonkyDocument(components=[
            make_component("disk_usage", enabled=False, properties={"mount_point": "relative/path"}),
        ])
        assert self.v.validate(doc) == []


# ---------------------------------------------------------------------------
# Validator — global settings errors
# ---------------------------------------------------------------------------


class TestValidatorSettingsErrors:
    def setup_method(self):
        self.v = Validator()

    def _settings_error_fields(self, settings: GlobalConkySettings) -> list[str]:
        doc = GonkyDocument(settings=settings)
        return [e.field for e in self.v.validate(doc) if e.severity == "error"]

    def test_negative_window_width_is_error(self):
        s = GlobalConkySettings(window_width=-1)
        assert "window_width" in self._settings_error_fields(s)

    def test_zero_window_width_is_valid(self):
        s = GlobalConkySettings(window_width=0)
        assert "window_width" not in self._settings_error_fields(s)

    def test_negative_gap_x_is_error(self):
        s = GlobalConkySettings(gap_x=-5)
        assert "gap_x" in self._settings_error_fields(s)

    def test_zero_gap_x_is_valid(self):
        s = GlobalConkySettings(gap_x=0)
        assert "gap_x" not in self._settings_error_fields(s)

    def test_negative_gap_y_is_error(self):
        s = GlobalConkySettings(gap_y=-1)
        assert "gap_y" in self._settings_error_fields(s)

    def test_zero_gap_y_is_valid(self):
        s = GlobalConkySettings(gap_y=0)
        assert "gap_y" not in self._settings_error_fields(s)

    def test_update_interval_too_low_is_error(self):
        s = GlobalConkySettings(update_interval=0.05)
        assert "update_interval" in self._settings_error_fields(s)

    def test_zero_update_interval_is_error(self):
        s = GlobalConkySettings(update_interval=0.0)
        assert "update_interval" in self._settings_error_fields(s)

    def test_negative_update_interval_is_error(self):
        s = GlobalConkySettings(update_interval=-1.0)
        assert "update_interval" in self._settings_error_fields(s)

    def test_minimum_update_interval_is_valid(self):
        s = GlobalConkySettings(update_interval=0.1)
        assert "update_interval" not in self._settings_error_fields(s)

    def test_empty_font_is_error(self):
        s = GlobalConkySettings(default_font="")
        assert "default_font" in self._settings_error_fields(s)

    def test_whitespace_font_is_error(self):
        s = GlobalConkySettings(default_font="   ")
        assert "default_font" in self._settings_error_fields(s)

    def test_valid_font_is_not_error(self):
        s = GlobalConkySettings(default_font="DejaVu Sans Mono")
        assert "default_font" not in self._settings_error_fields(s)

    def test_invalid_default_color_is_error(self):
        s = GlobalConkySettings(default_color="#ZZZZZZ")
        assert "default_color" in self._settings_error_fields(s)

    def test_valid_named_default_color_is_not_error(self):
        s = GlobalConkySettings(default_color="white")
        assert "default_color" not in self._settings_error_fields(s)

    def test_valid_hex_default_color_is_not_error(self):
        s = GlobalConkySettings(default_color="#ffffff")
        assert "default_color" not in self._settings_error_fields(s)

    def test_multiple_settings_errors_all_reported(self):
        s = GlobalConkySettings(window_width=-1, gap_x=-2, gap_y=-3)
        fields = self._settings_error_fields(s)
        assert "window_width" in fields
        assert "gap_x" in fields
        assert "gap_y" in fields

    def test_error_component_id_is_none_for_settings(self):
        s = GlobalConkySettings(window_width=-1)
        doc = GonkyDocument(settings=s)
        findings = self.v.validate(doc)
        for f in findings:
            assert f.component_id is None


# ---------------------------------------------------------------------------
# Validator — component property errors
# ---------------------------------------------------------------------------


class TestValidatorComponentErrors:
    def setup_method(self):
        self.v = Validator()

    def test_unknown_component_type_is_error(self):
        doc = GonkyDocument(components=[make_component("not_a_real_type")])
        findings = self.v.validate(doc)
        assert any(e.severity == "error" and e.field == "component_type" for e in findings)

    def test_invalid_mount_point_is_error(self):
        doc = GonkyDocument(components=[
            make_component("disk_usage", properties={"mount_point": "no_slash"})
        ])
        findings = self.v.validate(doc)
        assert any(e.field == "mount_point" and e.severity == "error" for e in findings)

    def test_valid_mount_point_not_error(self):
        doc = GonkyDocument(components=[
            make_component("disk_usage", properties={"mount_point": "/home"})
        ])
        assert self.v.validate(doc) == []

    def test_invalid_network_interface_with_space_is_error(self):
        doc = GonkyDocument(components=[
            make_component("net_upload", properties={"interface": "eth 0"})
        ])
        findings = self.v.validate(doc)
        assert any(e.field == "interface" and e.severity == "error" for e in findings)

    def test_empty_network_interface_is_error(self):
        doc = GonkyDocument(components=[
            make_component("net_upload", properties={"interface": ""})
        ])
        findings = self.v.validate(doc)
        assert any(e.field == "interface" and e.severity == "error" for e in findings)

    def test_valid_network_interface_not_error(self):
        doc = GonkyDocument(components=[
            make_component("net_upload", properties={"interface": "eth0"})
        ])
        assert self.v.validate(doc) == []

    def test_empty_command_is_error(self):
        doc = GonkyDocument(components=[
            make_component("exec", properties={"command": ""})
        ])
        findings = self.v.validate(doc)
        assert any(e.field == "command" and e.severity == "error" for e in findings)

    def test_non_empty_command_not_error(self):
        doc = GonkyDocument(components=[
            make_component("exec", properties={"command": "echo hi"})
        ])
        assert self.v.validate(doc) == []

    def test_component_id_is_set_in_component_errors(self):
        comp = make_component("disk_usage", properties={"mount_point": "bad"})
        doc = GonkyDocument(components=[comp])
        findings = self.v.validate(doc)
        error_findings = [e for e in findings if e.field == "mount_point"]
        assert len(error_findings) == 1
        assert error_findings[0].component_id == comp.id

    def test_invalid_color_in_component_is_error(self):
        doc = GonkyDocument(components=[
            make_component("net_upload_graph", properties={
                "color_lo": "#ZZZZZZ",
                "color_hi": "#ZZZZZZ",
            })
        ])
        findings = self.v.validate(doc)
        color_errors = [e for e in findings if e.field in ("color_lo", "color_hi") and e.severity == "error"]
        assert len(color_errors) >= 1

    def test_empty_color_in_component_not_error(self):
        # Empty string = "inherit" — must not be flagged.
        doc = GonkyDocument(components=[
            make_component("net_upload_graph", properties={"color_lo": "", "color_hi": ""})
        ])
        findings = self.v.validate(doc)
        assert not any(e.field in ("color_lo", "color_hi") for e in findings)

    def test_valid_color_in_component_not_error(self):
        doc = GonkyDocument(components=[
            make_component("net_upload_graph", properties={
                "color_lo": "#00ff00",
                "color_hi": "#ff0000",
            })
        ])
        assert self.v.validate(doc) == []

    def test_disabled_component_skipped_entirely(self):
        # Disabled component with invalid mount point must not produce findings.
        doc = GonkyDocument(components=[
            make_component("disk_usage", enabled=False, properties={"mount_point": "bad"})
        ])
        assert self.v.validate(doc) == []


# ---------------------------------------------------------------------------
# Validator — warning vs error severity
# ---------------------------------------------------------------------------


class TestValidatorWarnings:
    def setup_method(self):
        self.v = Validator()

    def test_unknown_named_colour_in_component_produces_warning(self):
        # "chartreuse" is purely alphabetic but not in _KNOWN_NAMED_COLOURS —
        # structurally valid (passes validate_color) but unknown, so a warning.
        doc = GonkyDocument(components=[
            make_component("net_upload_graph", properties={
                "color_lo": "chartreuse",
                "color_hi": "chartreuse",
            })
        ])
        findings = self.v.validate(doc)
        warnings = [f for f in findings if f.severity == "warning"]
        assert len(warnings) >= 1

    def test_known_named_colour_produces_no_warning(self):
        doc = GonkyDocument(components=[
            make_component("net_upload_graph", properties={
                "color_lo": "red",
                "color_hi": "green",
            })
        ])
        findings = self.v.validate(doc)
        colour_warnings = [f for f in findings if f.field in ("color_lo", "color_hi")]
        assert colour_warnings == []


# ---------------------------------------------------------------------------
# Validator — validate() returns all findings (settings + components)
# ---------------------------------------------------------------------------


class TestValidatorAllFindings:
    def setup_method(self):
        self.v = Validator()

    def test_settings_and_component_errors_both_returned(self):
        doc = GonkyDocument(
            settings=GlobalConkySettings(update_interval=0.0),
            components=[make_component("disk_usage", properties={"mount_point": "bad"})],
        )
        findings = self.v.validate(doc)
        fields = [f.field for f in findings]
        assert "update_interval" in fields
        assert "mount_point" in fields

    def test_multiple_components_all_checked(self):
        doc = GonkyDocument(components=[
            make_component("disk_usage", properties={"mount_point": "bad1"}),
            make_component("net_upload", properties={"interface": "bad iface"}),
        ])
        findings = self.v.validate(doc)
        fields = [f.field for f in findings]
        assert "mount_point" in fields
        assert "interface" in fields

    def test_returns_list_type(self):
        doc = GonkyDocument()
        result = self.v.validate(doc)
        assert isinstance(result, list)

    def test_empty_list_for_clean_document(self):
        doc = GonkyDocument()
        assert self.v.validate(doc) == []
