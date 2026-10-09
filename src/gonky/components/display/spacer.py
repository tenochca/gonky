"""Spacer component."""

from gonky.components.base import AbstractComponent, PropertyField


class Spacer(AbstractComponent):
    TYPE_KEY = "spacer"
    DISPLAY_NAME = "Spacer"
    ICON_NAME = "spacer"
    DEFAULT_PROPERTIES = {"line_count": 1}

    # reference format:
    # \n repeated line_count times
    def render_conky_text(self, props: dict) -> str:
        line_count: int = props.get("line_count", 1)
        if line_count < 1:
            line_count = 1
        return "\n" * line_count

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="line_count",
                label="Line Count",
                field_type="int",
                default=1,
                min_val=1,
                max_val=20,
                tooltip="Number of blank lines to insert",
            ),
        ]
