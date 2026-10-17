"""Integration tests — full pipeline from GonkyDocument through export (Sub-Task 11).

These tests verify the end-to-end flow:
  GonkyDocument  →  ConfigGenerator.generate()  →  FileManager.export_config()
  → written file read back → structural assertions on Conky Lua config syntax.
"""

import pytest

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

from gonky.logic.config_generator import ConfigGenerator, ConfigGenerationError
from gonky.logic.file_manager import export_config, load_project, save_project
from gonky.models.component import ConkyComponent
from gonky.models.document import GonkyDocument
from gonky.models.settings import GlobalConkySettings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_component(
    component_type: str,
    *,
    canvas_y: int = 0,
    canvas_x: int = 0,
    enabled: bool = True,
    properties: dict | None = None,
) -> ConkyComponent:
    return ConkyComponent(
        component_type=component_type,
        canvas_x=canvas_x,
        canvas_y=canvas_y,
        enabled=enabled,
        properties=properties or {},
    )


# ---------------------------------------------------------------------------
# TestConfigGeneratorIntegration — multi-component document in memory
# ---------------------------------------------------------------------------


class TestConfigGeneratorIntegration:
    """Test ConfigGenerator.generate() against realistic mixed documents."""

    def setup_method(self):
        self.gen = ConfigGenerator()

    def _doc_with(self, *component_types, settings=None):
        """Helper: build a GonkyDocument with the given ordered component types."""
        doc = GonkyDocument(settings=settings or GlobalConkySettings())
        for i, t in enumerate(component_types):
            doc.components.append(make_component(t, canvas_y=i * 10))
        return doc

    # --- structural validity ---

    def test_output_starts_with_conky_config(self):
        out = self.gen.generate(GonkyDocument())
        assert out.startswith("conky.config = {\n")

    def test_output_contains_conky_text_block(self):
        out = self.gen.generate(GonkyDocument())
        assert "conky.text = [[" in out
        assert out.endswith("]]")

    def test_config_block_precedes_text_block(self):
        out = self.gen.generate(GonkyDocument())
        assert out.index("conky.config") < out.index("conky.text")

    def test_closing_brace_before_conky_text(self):
        out = self.gen.generate(GonkyDocument())
        assert out.index("}\n") < out.index("conky.text")

    # --- five mixed components ---

    def test_five_mixed_components_all_present(self):
        """Core acceptance criterion: 5 mixed components each appear in the output."""
        doc = self._doc_with(
            "cpu_usage",
            "ram_usage",
            "separator",
            "clock",
            "spacer",
        )
        out = self.gen.generate(doc)
        assert "${cpu}" in out
        assert "${memperc}" in out
        assert "${hr}" in out
        assert "${time" in out

    def test_component_order_follows_canvas_y(self):
        """Components should appear in canvas_y ascending order."""
        doc = GonkyDocument()
        doc.components.append(make_component("separator", canvas_y=30))
        doc.components.append(make_component("cpu_usage", canvas_y=0))
        doc.components.append(make_component("ram_usage", canvas_y=15))
        out = self.gen.generate(doc)
        assert out.index("${cpu}") < out.index("${memperc}") < out.index("${hr}")

    def test_x_tiebreaker_when_y_equal(self):
        doc = GonkyDocument()
        doc.components.append(make_component("separator", canvas_y=0, canvas_x=20))
        doc.components.append(make_component("cpu_usage", canvas_y=0, canvas_x=5))
        out = self.gen.generate(doc)
        assert out.index("${cpu}") < out.index("${hr}")

    def test_disabled_component_absent_from_output(self):
        doc = self._doc_with("cpu_usage", "ram_usage")
        doc.components[1].enabled = False
        out = self.gen.generate(doc)
        assert "${cpu}" in out
        assert "${memperc}" not in out

    def test_settings_reflected_in_config_block(self):
        settings = GlobalConkySettings(
            alignment="bottom_right",
            gap_x=5,
            gap_y=5,
            default_font="Roboto Mono",
            default_font_size=11,
            update_interval=2.0,
        )
        doc = GonkyDocument(settings=settings)
        out = self.gen.generate(doc)
        assert "alignment = 'bottom_right'" in out
        assert "gap_x = 5" in out
        assert "font = 'Roboto Mono:size=11'" in out
        assert "update_interval = 2.0" in out

    def test_extra_lua_between_config_and_text(self):
        lua = "-- injected lua\nfunction my_fn() end"
        doc = GonkyDocument(settings=GlobalConkySettings(extra_lua=lua))
        out = self.gen.generate(doc)
        config_pos = out.index("conky.config")
        lua_pos = out.index("injected lua")
        text_pos = out.index("conky.text")
        assert config_pos < lua_pos < text_pos

    def test_no_extra_lua_omitted_from_output(self):
        doc = GonkyDocument(settings=GlobalConkySettings(extra_lua=""))
        out = self.gen.generate(doc)
        assert "extra_lua" not in out

    # --- component-specific Conky variable assertions ---

    def test_cpu_bar_with_custom_properties(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("cpu_bar", properties={"height": 6, "width": 200})
        )
        out = self.gen.generate(doc)
        assert "${cpubar 6,200}" in out

    def test_net_download_uses_interface(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("net_download", properties={"interface": "wlan0"})
        )
        out = self.gen.generate(doc)
        assert "${downspeed wlan0}" in out

    def test_disk_usage_with_mount_point(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("disk_usage", properties={"mount_point": "/home", "format": "%"})
        )
        out = self.gen.generate(doc)
        assert "${fs_used_perc /home}" in out

    def test_custom_text_dollar_escaped(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("text", properties={"content": "worth $10"})
        )
        out = self.gen.generate(doc)
        assert r"\$10" in out

    def test_custom_text_font_wrapper_intact(self):
        """The ${font ...} wrapper around custom text must survive generation."""
        doc = GonkyDocument()
        doc.components.append(make_component("text", properties={"content": "hello"}))
        out = self.gen.generate(doc)
        assert "${font" in out

    def test_spacer_line_count_respected(self):
        """Spacer with line_count=3 should produce exactly three newlines in the body."""
        doc = GonkyDocument()
        doc.components.append(
            make_component("spacer", properties={"line_count": 3})
        )
        out = self.gen.generate(doc)
        body = out[out.index("conky.text = [[\n") + len("conky.text = [[\n"):-len("]]")]
        assert body == "\n\n\n"

    def test_battery_percent_component(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("battery_percent", properties={"battery_id": "BAT1"})
        )
        out = self.gen.generate(doc)
        assert "${battery_percent BAT1}" in out

    def test_exec_command_component(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("exec", properties={"command": "hostname", "exec_type": "exec"})
        )
        out = self.gen.generate(doc)
        assert "${exec hostname}" in out

    def test_lua_snippet_passthrough(self):
        doc = GonkyDocument()
        doc.components.append(
            make_component("lua_snippet", properties={"raw_text": "${lua my_func 42}"})
        )
        out = self.gen.generate(doc)
        assert "${lua my_func 42}" in out

    # --- error paths ---

    def test_unknown_component_type_raises(self):
        doc = GonkyDocument()
        doc.components.append(make_component("does_not_exist"))
        with pytest.raises(ConfigGenerationError):
            self.gen.generate(doc)

    def test_zero_update_interval_raises(self):
        doc = GonkyDocument(settings=GlobalConkySettings(update_interval=0.0))
        with pytest.raises(ConfigGenerationError, match="update_interval"):
            self.gen.generate(doc)

    def test_empty_font_raises(self):
        doc = GonkyDocument(settings=GlobalConkySettings(default_font=""))
        with pytest.raises(ConfigGenerationError, match="default_font"):
            self.gen.generate(doc)


# ---------------------------------------------------------------------------
# TestExportAndReadBack — writes to disk and reads the file back
# ---------------------------------------------------------------------------


class TestExportAndReadBack:
    """Construct a document, export it to a temp file, then read the file back
    and assert structural validity of the Conky Lua config."""

    def _make_rich_document(self) -> GonkyDocument:
        """Return a GonkyDocument with 5 mixed component types."""
        doc = GonkyDocument(
            project_name="Integration Test",
            settings=GlobalConkySettings(
                alignment="top_right",
                gap_x=15,
                gap_y=15,
                default_font="DejaVu Sans Mono",
                default_font_size=10,
                update_interval=1.5,
                default_color="white",
            ),
        )
        doc.components.extend([
            make_component("cpu_usage",      canvas_y=0),
            make_component("ram_usage",      canvas_y=10),
            make_component("separator",      canvas_y=20),
            make_component("clock",          canvas_y=30),
            make_component("battery_percent", canvas_y=40),
        ])
        return doc

    def test_export_produces_valid_config_file(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        assert path.exists()

    def test_exported_file_has_config_block_header(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert "conky.config = {" in content

    def test_exported_file_has_text_block_header(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert "conky.text = [[" in content

    def test_exported_file_has_text_block_footer(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert content.endswith("]]")

    def test_exported_file_contains_cpu_variable(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        assert "${cpu}" in path.read_text(encoding="utf-8")

    def test_exported_file_contains_ram_variable(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        assert "${memperc}" in path.read_text(encoding="utf-8")

    def test_exported_file_contains_separator_variable(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        assert "${hr}" in path.read_text(encoding="utf-8")

    def test_exported_file_contains_clock_variable(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        assert "${time" in path.read_text(encoding="utf-8")

    def test_exported_file_contains_battery_variable(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        assert "${battery_percent" in path.read_text(encoding="utf-8")

    def test_exported_settings_embedded_in_config_block(self, tmp_path):
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert "alignment = 'top_right'" in content
        assert "gap_x = 15" in content
        assert "gap_y = 15" in content
        assert "font = 'DejaVu Sans Mono:size=10'" in content
        assert "update_interval = 1.5" in content

    def test_component_order_in_exported_file(self, tmp_path):
        """Components placed at increasing Y must appear in that order in the file."""
        doc = self._make_rich_document()
        path = tmp_path / "conky.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        # cpu_usage (y=0) < ram_usage (y=10) < separator (y=20) < clock (y=30) < battery (y=40)
        positions = [
            content.index("${cpu}"),
            content.index("${memperc}"),
            content.index("${hr}"),
            content.index("${time"),
            content.index("${battery_percent"),
        ]
        assert positions == sorted(positions), "Components not in ascending Y order in output"

    def test_disabled_component_absent_from_exported_file(self, tmp_path):
        doc = GonkyDocument()
        doc.components.append(make_component("cpu_usage", canvas_y=0, enabled=True))
        doc.components.append(make_component("ram_usage", canvas_y=10, enabled=False))
        path = tmp_path / "partial.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert "${cpu}" in content
        assert "${memperc}" not in content

    def test_save_then_load_then_export_is_consistent(self, tmp_path):
        """Full round-trip: save → load → export → read back."""
        original = self._make_rich_document()

        # Save the project file
        project_path = tmp_path / "project"
        save_project(original, project_path)

        # Load it back
        restored = load_project(tmp_path / "project.gonky")
        assert restored.project_name == "Integration Test"
        assert len(restored.components) == 5

        # Export the restored document
        conf_path = tmp_path / "restored.conf"
        export_config(restored, conf_path)
        content = conf_path.read_text(encoding="utf-8")

        # Structural assertions
        assert "conky.config = {" in content
        assert "conky.text = [[" in content
        assert "${cpu}" in content
        assert "${memperc}" in content
        assert "${hr}" in content
        assert "${time" in content
        assert "${battery_percent" in content
        assert content.endswith("]]")
