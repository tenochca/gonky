"""Generic bar component."""

from gonky.components.base import AbstractComponent, PropertyField


class GenericBar(AbstractComponent):
    TYPE_KEY = "bar"
    DISPLAY_NAME = "Generic Bar"
    ICON_NAME = "bar"
    DEFAULT_PROPERTIES = {
        "variable_expr": "",
        "width": 0,
        "height": 0,
    }

    # reference format (width and height are optional):
    # ${bar h,w variable}
    def render_conky_text(self, props: dict) -> str:
        variable_expr: str = props.get("variable_expr", "")
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)

        var = "bar"
        if height != 0:
            var += f" {height}"
            if width != 0:
                var += f",{width}"
        if variable_expr:
            var += f" {variable_expr}"
        return f"${{{var}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="variable_expr",
                label="Variable Expression",
                field_type="text",
                default="",
                tooltip="Conky variable to use as the bar value, e.g. cpu or memperc",
            ),
            PropertyField(
                key="width",
                label="Width",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Bar width in pixels; 0 = use Conky's default bar width",
            ),
            PropertyField(
                key="height",
                label="Height",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Bar height in pixels; 0 = use Conky's default bar height",
            ),
        ]
