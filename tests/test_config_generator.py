"""Unit tests for ConfigGenerator (Sub-Task 6)."""

import pytest

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

from gonky.logic.config_generator import ConfigGenerationError, ConfigGenerator
from gonky.models.component import ConkyComponent, COMPONENT_REGISTRY
from gonky.models.document import GonkyDocument
from gonky.models.settings import GlobalConkySettings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_component(component_type: str, *, canvas_x: int = 0, canvas_y: int = 0,
                   enabled: bool = True, properties: dict | None = None) -> ConkyComponent:
    return ConkyComponent(
        component_type=component_type,
        canvas_x=canvas_x,
        canvas_y=canvas_y,
        enabled=enabled,
        properties=properties or {},
    )


# ---------------------------------------------------------------------------
# TestRenderConfigBlock
# ---------------------------------------------------------------------------

class TestRenderConfigBlock:
    def setup_method(self):
        self.gen = ConfigGenerator()
        self.default = GlobalConkySettings()

    def test_opens_and_closes_with_braces(self):
        out = self.gen._render_config_block(self.default)
        assert out.startswith("conky.config = {\n")
        assert out.endswith("}\n")

    def test_default_settings_alignment(self):
        out = self.gen._render_config_block(self.default)
        assert "    alignment = 'top_left'," in out

    def test_default_settings_gap(self):
        out = self.gen._render_config_block(self.default)
        assert "    gap_x = 10," in out
        assert "    gap_y = 10," in out

    def test_window_width_emitted_as_minimum_width(self):
        out = self.gen._render_config_block(self.default)
        assert "    minimum_width = 300," in out
        assert "window_width" not in out

    def test_window_height_emitted_as_minimum_height(self):
        out = self.gen._render_config_block(self.default)
        assert "    minimum_height = 0," in out
        assert "window_height" not in out

    def test_booleans_render_as_lua_literals(self):
        out = self.gen._render_config_block(self.default)
        assert "    own_window = true," in out
        assert "    own_window_transparent = true," in out
        assert "    own_window_argb_visual = true," in out
        assert "    double_buffer = true," in out
        assert "    background = false," in out

    def test_false_bool_renders_lowercase(self):
        settings = GlobalConkySettings(own_window=False, background=True)
        out = self.gen._render_config_block(settings)
        assert "    own_window = false," in out
        assert "    background = true," in out

    def test_font_combined_as_single_key(self):
        out = self.gen._render_config_block(self.default)
        assert "    font = 'DejaVu Sans Mono:size=10'," in out
        assert "default_font" not in out
        assert "default_font_size" not in out

    def test_custom_font_and_size(self):
        settings = GlobalConkySettings(default_font="Noto Sans", default_font_size=12)
        out = self.gen._render_config_block(settings)
        assert "    font = 'Noto Sans:size=12'," in out

    def test_default_color(self):
        out = self.gen._render_config_block(self.default)
        assert "    default_color = 'white'," in out

    def test_update_interval_float(self):
        settings = GlobalConkySettings(update_interval=2.5)
        out = self.gen._render_config_block(settings)
        assert "    update_interval = 2.5," in out

    def test_extra_lua_absent_from_config_block(self):
        settings = GlobalConkySettings(extra_lua="-- some lua\n")
        out = self.gen._render_config_block(settings)
        assert "some lua" not in out

    def test_border_width_and_avg_samples(self):
        out = self.gen._render_config_block(self.default)
        assert "    border_width = 0," in out
        assert "    cpu_avg_samples = 2," in out
        assert "    net_avg_samples = 2," in out

    def test_background_key_not_own_window_background(self):
        """Regression: the Lua key must be 'background', not 'own_window_background'."""
        out = self.gen._render_config_block(self.default)
        assert "own_window_background" not in out
        assert "    background = " in out

    def test_own_window_colour_omitted_when_transparent(self):
        """own_window_colour must not appear in the config when transparency is on."""
        settings = GlobalConkySettings(own_window_transparent=True, own_window_colour="#1a1a2e")
        out = self.gen._render_config_block(settings)
        assert "own_window_colour" not in out

    def test_own_window_colour_omitted_when_colour_empty(self):
        """own_window_colour must not appear when the colour field is empty string."""
        settings = GlobalConkySettings(own_window_transparent=False, own_window_colour="")
        out = self.gen._render_config_block(settings)
        assert "own_window_colour" not in out

    def test_own_window_colour_emitted_when_transparency_disabled(self):
        """own_window_colour must appear when transparency is off and a colour is set."""
        settings = GlobalConkySettings(own_window_transparent=False, own_window_colour="#1a1a2e")
        out = self.gen._render_config_block(settings)
        assert "    own_window_colour = '#1a1a2e'," in out


# ---------------------------------------------------------------------------
# TestSortComponents
# ---------------------------------------------------------------------------

class TestSortComponents:
    def setup_method(self):
        self.gen = ConfigGenerator()

    def test_sorts_ascending_by_y(self):
        c1 = make_component("cpu_usage", canvas_y=10)
        c2 = make_component("cpu_usage", canvas_y=5)
        c3 = make_component("cpu_usage", canvas_y=20)
        result = self.gen._sort_components([c1, c2, c3])
        assert [r.canvas_y for r in result] == [5, 10, 20]

    def test_x_is_tiebreaker(self):
        c1 = make_component("cpu_usage", canvas_y=0, canvas_x=20)
        c2 = make_component("cpu_usage", canvas_y=0, canvas_x=5)
        result = self.gen._sort_components([c1, c2])
        assert result[0].canvas_x == 5
        assert result[1].canvas_x == 20

    def test_disabled_components_excluded(self):
        enabled = make_component("cpu_usage", enabled=True)
        disabled = make_component("cpu_usage", enabled=False)
        result = self.gen._sort_components([enabled, disabled])
        assert len(result) == 1
        assert result[0] is enabled

    def test_empty_list_returns_empty_list(self):
        assert self.gen._sort_components([]) == []

    def test_input_list_is_not_mutated(self):
        c1 = make_component("cpu_usage", canvas_y=10)
        c2 = make_component("cpu_usage", canvas_y=5)
        original = [c1, c2]
        self.gen._sort_components(original)
        assert original == [c1, c2]


# ---------------------------------------------------------------------------
# TestEscapeConkyText
# ---------------------------------------------------------------------------

class TestEscapeConkyText:
    def setup_method(self):
        self.gen = ConfigGenerator()

    def test_dollar_sign_escaped(self):
        assert self.gen._escape_conky_text("costs $5") == r"costs \$5"

    def test_dollar_brace_sequence_escaped(self):
        assert self.gen._escape_conky_text("${foo}") == r"\${foo}"

    def test_no_dollars_unchanged(self):
        assert self.gen._escape_conky_text("no dollars") == "no dollars"

    def test_empty_string_unchanged(self):
        assert self.gen._escape_conky_text("") == ""

    def test_multiple_dollars(self):
        assert self.gen._escape_conky_text("$a and $b") == r"\$a and \$b"


# ---------------------------------------------------------------------------
# TestRenderTextBlock
# ---------------------------------------------------------------------------

class TestRenderTextBlock:
    def setup_method(self):
        self.gen = ConfigGenerator()

    def _render(self, components):
        return self.gen._render_text_block(components)

    def test_empty_components_produces_valid_skeleton(self):
        out = self._render([])
        assert out == "conky.text = [[\n]]"

    def test_cpu_usage_component(self):
        c = make_component("cpu_usage")
        out = self._render([c])
        assert "conky.text = [[\n" in out
        assert "${cpu}" in out

    def test_ram_usage_component(self):
        c = make_component("ram_usage")
        out = self._render([c])
        assert "${memperc}" in out

    def test_ram_bar_component(self):
        c = make_component("ram_bar")
        out = self._render([c])
        assert "${membar" in out

    def test_disk_usage_component(self):
        c = make_component("disk_usage")
        out = self._render([c])
        assert "${fs_used_perc" in out

    def test_network_download_component(self):
        c = make_component("net_download")
        out = self._render([c])
        assert "${downspeed" in out

    def test_battery_percent_component(self):
        c = make_component("battery_percent")
        out = self._render([c])
        assert "${battery_percent" in out

    def test_temperature_component(self):
        c = make_component("temperature")
        out = self._render([c])
        assert "${hwmon" in out or "${acpitemp}" in out or "temp" in out.lower()

    def test_process_count_component(self):
        # Default count_type="running" renders ${running_processes}
        c = make_component("process_count")
        out = self._render([c])
        assert "${running_processes}" in out

    def test_process_count_total(self):
        c = make_component("process_count", properties={"count_type": "total"})
        out = self._render([c])
        assert "${processes}" in out

    def test_clock_component(self):
        c = make_component("clock")
        out = self._render([c])
        assert "${time" in out

    def test_date_component(self):
        c = make_component("date")
        out = self._render([c])
        assert "${time" in out

    def test_uptime_component(self):
        c = make_component("uptime")
        out = self._render([c])
        assert "${uptime" in out

    def test_separator_component(self):
        c = make_component("separator")
        out = self._render([c])
        assert "${hr}" in out

    def test_exec_component(self):
        c = make_component("exec", properties={"command": "echo hi"})
        out = self._render([c])
        assert "${exec" in out

    def test_lua_snippet_component(self):
        # LuaSnippet injects raw_text verbatim — pass Conky lua syntax directly
        c = make_component("lua_snippet", properties={"raw_text": "${lua my_fn 1}"})
        out = self._render([c])
        assert "${lua my_fn 1}" in out

    def test_spacer_adds_blank_lines(self):
        c = make_component("spacer", properties={"line_count": 2})
        out = self._render([c])
        # Spacer with line_count=2 should produce two newlines in the body
        body = out[len("conky.text = [[\n"):-len("]]")]
        assert body == "\n\n"

    def test_custom_text_content_dollar_escaped(self):
        """Literal $ in CustomText content must be escaped; ${font ...} wrapper must not be."""
        c = make_component("text", properties={"content": "price $10"})
        out = self._render([c])
        # The escaped content should appear
        assert r"\$10" in out
        # The ${font ...} wrapping from render_conky_text must remain intact
        assert "${font" in out

    def test_custom_text_with_no_dollar_unchanged(self):
        c = make_component("text", properties={"content": "hello world"})
        out = self._render([c])
        assert "hello world" in out

    def test_default_properties_merged_with_component_properties(self):
        """Component properties should override DEFAULT_PROPERTIES, not replace them."""
        # CpuUsage default core=0; override with core=1
        c = make_component("cpu_usage", properties={"core": 1})
        out = self._render([c])
        assert "cpu1" in out

    def test_unknown_component_type_raises(self):
        c = make_component("totally_unknown_type")
        with pytest.raises(ConfigGenerationError, match="totally_unknown_type"):
            self._render([c])

    def test_non_spacer_components_separated_by_newlines(self):
        c1 = make_component("cpu_usage", canvas_y=0)
        c2 = make_component("ram_usage", canvas_y=1)
        out = self._render([c1, c2])
        body = out[len("conky.text = [[\n"):-len("]]")]
        lines = body.split("\n")
        # Each component line ends with \n, so we get one line per component
        assert len([ln for ln in lines if ln.strip()]) == 2

    def test_output_starts_with_conky_text_marker(self):
        out = self._render([])
        assert out.startswith("conky.text = [[")

    def test_output_ends_with_closing_brackets(self):
        out = self._render([])
        assert out.endswith("]]")


# ---------------------------------------------------------------------------
# TestGenerate (integration)
# ---------------------------------------------------------------------------

class TestGenerate:
    def setup_method(self):
        self.gen = ConfigGenerator()

    def test_empty_document_produces_valid_skeleton(self):
        doc = GonkyDocument()
        out = self.gen.generate(doc)
        assert "conky.config = {" in out
        assert "conky.text = [[" in out
        assert "]]" in out

    def test_config_block_precedes_text_block(self):
        doc = GonkyDocument()
        out = self.gen.generate(doc)
        assert out.index("conky.config") < out.index("conky.text")

    def test_full_document_with_mixed_components(self):
        doc = GonkyDocument(
            settings=GlobalConkySettings(default_font="Noto Mono", default_font_size=11),
            components=[
                make_component("cpu_usage", canvas_y=0),
                make_component("ram_usage", canvas_y=1),
                make_component("spacer", canvas_y=2),
                make_component("separator", canvas_y=3),
            ],
        )
        out = self.gen.generate(doc)
        assert "conky.config = {" in out
        assert "font = 'Noto Mono:size=11'" in out
        assert "${cpu}" in out
        assert "${memperc}" in out
        assert "${hr}" in out

    def test_extra_lua_appears_between_config_and_text(self):
        lua = "-- custom lua\nconky_lua = 1"
        doc = GonkyDocument(settings=GlobalConkySettings(extra_lua=lua))
        out = self.gen.generate(doc)
        config_pos = out.index("conky.config")
        lua_pos = out.index("custom lua")
        text_pos = out.index("conky.text")
        assert config_pos < lua_pos < text_pos

    def test_no_extra_lua_emits_no_blank_extra_lines(self):
        doc = GonkyDocument(settings=GlobalConkySettings(extra_lua=""))
        out = self.gen.generate(doc)
        assert "extra_lua" not in out
        # config block and text block separated by exactly one blank line
        config_end = out.index("}\n") + len("}\n")
        text_start = out.index("conky.text")
        separator = out[config_end:text_start]
        assert separator == "\n"

    def test_disabled_components_absent_from_output(self):
        doc = GonkyDocument(components=[
            make_component("cpu_usage", enabled=True, canvas_y=0),
            make_component("ram_usage", enabled=False, canvas_y=1),
        ])
        out = self.gen.generate(doc)
        assert "${cpu}" in out
        assert "${memperc}" not in out

    def test_components_sorted_by_y_in_output(self):
        doc = GonkyDocument(components=[
            make_component("ram_usage", canvas_y=10),
            make_component("cpu_usage", canvas_y=5),
        ])
        out = self.gen.generate(doc)
        cpu_pos = out.index("${cpu}")
        mem_pos = out.index("${memperc}")
        assert cpu_pos < mem_pos

    def test_invalid_update_interval_raises(self):
        doc = GonkyDocument(settings=GlobalConkySettings(update_interval=0))
        with pytest.raises(ConfigGenerationError, match="update_interval"):
            self.gen.generate(doc)

    def test_negative_update_interval_raises(self):
        doc = GonkyDocument(settings=GlobalConkySettings(update_interval=-1.0))
        with pytest.raises(ConfigGenerationError):
            self.gen.generate(doc)

    def test_empty_default_font_raises(self):
        doc = GonkyDocument(settings=GlobalConkySettings(default_font=""))
        with pytest.raises(ConfigGenerationError, match="default_font"):
            self.gen.generate(doc)

    def test_unknown_component_type_raises(self):
        doc = GonkyDocument(components=[make_component("not_a_real_type")])
        with pytest.raises(ConfigGenerationError):
            self.gen.generate(doc)
