"""Raw Conky/Lua text injection component."""

from gonky.components.base import AbstractComponent, PropertyField


class LuaSnippet(AbstractComponent):
    TYPE_KEY = "lua_snippet"
    DISPLAY_NAME = "Raw Conky/Lua Text"
    ICON_NAME = "lua_snippet"
    DEFAULT_PROPERTIES = {"raw_text": ""}

    # reference format:
    # Literal text injected verbatim into conky.text
    def render_conky_text(self, props: dict) -> str:
        raw_text: str = props.get("raw_text", "")
        return raw_text

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="raw_text",
                label="Raw Text",
                field_type="text",
                default="",
                tooltip="Text injected verbatim into conky.text; supports Conky variables and Lua expressions",
            ),
        ]
