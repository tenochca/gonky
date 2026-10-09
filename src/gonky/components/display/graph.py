"""Generic graph component."""

from gonky.components.base import AbstractComponent, PropertyField


class GenericGraph(AbstractComponent):
    TYPE_KEY = "graph"
    DISPLAY_NAME = "Generic Graph"
    ICON_NAME = "graph"
    DEFAULT_PROPERTIES = {
        "variable_expr": "",
        "width": 0,
        "height": 0,
        "color_lo": "",
        "color_hi": "",
    }

    # reference format (all args optional):
    # ${graph variable h,w color_lo color_hi}
    def render_conky_text(self, props: dict) -> str:
        variable_expr: str = props.get("variable_expr", "")
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color_lo: str = props.get("color_lo", "")
        color_hi: str = props.get("color_hi", "")

        var = "graph"
        if variable_expr:
            var += f" {variable_expr}"
        if height != 0:
            var += f" {height}"
            if width != 0:
                var += f",{width}"
        # Conky requires both colors together or neither
        if color_lo != "" and color_hi != "":
            var += f" {color_lo} {color_hi}"
        return f"${{{var}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="variable_expr",
                label="Variable Expression",
                field_type="text",
                default="",
                tooltip="Conky variable to graph, e.g. cpu or memperc",
            ),
            PropertyField(
                key="width",
                label="Width",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Graph width in pixels; 0 = use Conky's default graph width",
            ),
            PropertyField(
                key="height",
                label="Height",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Graph height in pixels; 0 = use Conky's default graph height",
            ),
            PropertyField(
                key="color_lo",
                label="Color Low",
                field_type="color",
                default="",
                tooltip="Graph color at low value; both colors must be set together",
            ),
            PropertyField(
                key="color_hi",
                label="Color High",
                field_type="color",
                default="",
                tooltip="Graph color at high value; both colors must be set together",
            ),
        ]
