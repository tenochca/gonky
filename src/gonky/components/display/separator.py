"""Separator component."""

from gonky.components.base import AbstractComponent, PropertyField


class Separator(AbstractComponent):
    TYPE_KEY = "separator"
    DISPLAY_NAME = "Separator Line"
    ICON_NAME = "separator"
    DEFAULT_PROPERTIES = {"width": 0, "color": ""}

    # reference format (width and color are optional):
    # ${hr N}
    # ${color red}${hr N}${color}
    def render_conky_text(self, props: dict) -> str:
        width: int = props.get("width", 0)
        color: str = props.get("color", "")

        var = "hr"
        if width != 0:
            var += f" {width}"

        if color != "":
            return f"${{color {color}}}${{{var}}}${{color}}"
        return f"${{{var}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="width",
                label="Width",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Separator line height in pixels; 0 = use Conky's default",
            ),
            PropertyField(
                key="color",
                label="Color",
                field_type="color",
                default="",
                tooltip="Leave empty to inherit the current Conky color",
            ),
        ]
