"""Custom text component."""

from gonky.components.base import AbstractComponent, PropertyField


class CustomText(AbstractComponent):
    TYPE_KEY = "text"
    DISPLAY_NAME = "Custom Text"
    ICON_NAME = "text"
    DEFAULT_PROPERTIES = {
        "content": "",
        "color": "",
        "font": "DejaVu Sans Mono",
        "size": 10,
    }

    # reference format:
    # ${font Name:size=N}text${font}
    # ${color #rrggbb}${font Name:size=N}text${font}${color}
    def render_conky_text(self, props: dict) -> str:
        content: str = props.get("content", "")
        color: str = props.get("color", "")
        font: str = props.get("font", "DejaVu Sans Mono")
        size: int = props.get("size", 10)

        var = f"${{font {font}:size={size}}}{content}${{font}}"
        if color != "":
            return f"${{color {color}}}{var}${{color}}"
        return var

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="content",
                label="Text Content",
                field_type="text",
                default="",
                tooltip="Literal text to display; use \\$ to show a dollar sign",
            ),
            PropertyField(
                key="color",
                label="Color",
                field_type="color",
                default="",
                tooltip="Leave empty to inherit the current Conky color",
            ),
            PropertyField(
                key="font",
                label="Font",
                field_type="font",
                default="DejaVu Sans Mono",
                tooltip="Font used for this text block; overrides the global Conky font",
            ),
            PropertyField(
                key="size",
                label="Font Size",
                field_type="int",
                default=10,
                min_val=1,
                max_val=None,
                tooltip="Font size in points",
            ),
        ]
