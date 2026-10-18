"""Config generator — translates a GonkyDocument into a Conky Lua config string."""

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

from gonky.models.component import COMPONENT_REGISTRY, ConkyComponent
from gonky.models.document import GonkyDocument
from gonky.models.settings import GlobalConkySettings


class ConfigGenerationError(Exception):
    """Raised when document state prevents a valid Conky config from being generated."""


class ConfigGenerator:
    def generate(self, doc: GonkyDocument) -> str:
        """Validate the document and return a complete Conky Lua config string."""
        self._validate_before_generate(doc)
        config_block = self._render_config_block(doc.settings)
        text_block = self._render_text_block(doc.components)

        # extra_lua is appended verbatim between the config block and conky.text,
        # separated by blank lines on each side. Omitted entirely when empty.
        if doc.settings.extra_lua:
            return f"{config_block}\n{doc.settings.extra_lua}\n\n{text_block}"
        return f"{config_block}\n{text_block}"

    def _render_config_block(self, settings: GlobalConkySettings) -> str:
        """Convert GlobalConkySettings into a complete conky.config = { ... } block.

        Field order matches the canonical Conky example in the implementation plan.
        extra_lua is NOT emitted here — generate() appends it after the closing brace.
        """
        def b(val: bool) -> str:
            """Format a Python bool as a Lua boolean literal."""
            return "true" if val else "false"

        config = "conky.config = {\n"
        config += f"    alignment = '{settings.alignment}',\n"
        config += f"    gap_x = {settings.gap_x},\n"
        config += f"    gap_y = {settings.gap_y},\n"
        config += f"    minimum_width = {settings.window_width},\n"
        config += f"    minimum_height = {settings.window_height},\n"
        config += f"    own_window = {b(settings.own_window)},\n"
        config += f"    own_window_type = '{settings.own_window_type}',\n"
        config += f"    own_window_transparent = {b(settings.own_window_transparent)},\n"
        config += f"    own_window_argb_visual = {b(settings.own_window_argb_visual)},\n"
        if not settings.own_window_transparent and settings.own_window_colour:
            config += f"    own_window_colour = '{settings.own_window_colour}',\n"
        config += f"    double_buffer = {b(settings.double_buffer)},\n"
        config += f"    update_interval = {settings.update_interval},\n"
        config += f"    font = '{settings.default_font}:size={settings.default_font_size}',\n"
        config += f"    default_color = '{settings.default_color}',\n"
        config += f"    background = {b(settings.background)},\n"
        config += f"    border_width = {settings.border_width},\n"
        config += f"    cpu_avg_samples = {settings.cpu_avg_samples},\n"
        config += f"    net_avg_samples = {settings.net_avg_samples},\n"
        config += f"    use_xft = {b(settings.use_xft)},\n"
        config += "}\n"
        return config

    def _sort_components(self, components: list[ConkyComponent]) -> list[ConkyComponent]:
        """Return enabled components sorted ascending by canvas_y, then canvas_x."""
        sorted_components = sorted(components, key=lambda c: (c.canvas_y, c.canvas_x))
        return [c for c in sorted_components if c.enabled]

    def _escape_conky_text(self, text: str) -> str:
        """Escape literal dollar signs so Conky does not interpret them as variables.

        Only the `content` property of CustomText components should be passed here,
        never the full rendered fragment (which contains intentional ${...} syntax).
        """
        return text.replace("$", "\\$")

    def _render_text_block(self, components: list[ConkyComponent]) -> str:
        """Render all enabled components into a conky.text = [[ ... ]] block.

        Components are output in Y-ascending order (X as tiebreaker).
        Spacer components control blank-line count directly via their render output.
        CustomText content is dollar-escaped before rendering; all other components
        emit raw Conky variable syntax and must never be passed through the escaper.
        Unknown component types raise ConfigGenerationError.
        """
        sorted_components = self._sort_components(components)

        lines: list[str] = []
        for component in sorted_components:
            if component.component_type not in COMPONENT_REGISTRY:
                raise ConfigGenerationError(
                    f"Unknown component type '{component.component_type}' — "
                    "not present in COMPONENT_REGISTRY."
                )

            cls = COMPONENT_REGISTRY[component.component_type]
            instance = cls()
            props = {**cls.DEFAULT_PROPERTIES, **component.properties}

            if component.component_type == "text":
                # Escape the user-typed content before rendering so literal '$'
                # characters are not treated as Conky variable references.
                props = dict(props)
                props["content"] = self._escape_conky_text(props.get("content", ""))

            conky_text = instance.render_conky_text(props)

            if component.component_type == "spacer":
                # Spacer.render_conky_text() returns '\n' * line_count; append as-is
                # so the correct number of blank lines appears in the output.
                lines.append(conky_text)
            else:
                lines.append(conky_text + "\n")

        return "conky.text = [[\n" + "".join(lines) + "]]"

    def _validate_before_generate(self, doc: GonkyDocument) -> None:
        """Raise ConfigGenerationError if the document cannot produce a valid config.

        Checks performed:
        - doc.settings is not None
        - all component_type values are registered in COMPONENT_REGISTRY
        - update_interval is greater than 0 (Conky crashes on 0 or negative values)
        - default_font is not an empty string
        """
        if doc.settings is None:
            raise ConfigGenerationError("Document settings must not be None.")
        for component in doc.components:
            if component.component_type not in COMPONENT_REGISTRY:
                raise ConfigGenerationError(
                    f"Component type '{component.component_type}' is not in COMPONENT_REGISTRY."
                )
        if doc.settings.update_interval <= 0:
            raise ConfigGenerationError(
                f"update_interval must be greater than 0, got {doc.settings.update_interval}."
            )
        if doc.settings.default_font == "":
            raise ConfigGenerationError("default_font must not be an empty string.")
