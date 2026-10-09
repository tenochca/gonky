"""Memory components."""

from gonky.components.base import AbstractComponent, PropertyField


class RamUsage(AbstractComponent):
    TYPE_KEY = "ram_usage"
    DISPLAY_NAME = "RAM Usage"
    ICON_NAME = "ram_usage"
    DEFAULT_PROPERTIES = {"format": "%"}

    # reference format (differs depending on choice)
    # ${memperc} -- percentage
    # ${mem} -- GB used (human)
    # ${memraw} -- bytes used
    def render_conky_text(self, props: dict) -> str:
        format: str = props.get("format", "%")

        if format == "human":
            return f"${{mem}}"
        elif format == "bytes":
            return f"${{memraw}}"
        else:
            return f"${{memperc}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="format",
                label="Format",
                field_type="choice",
                default="%",
                choices=["%", "bytes", "human"],
                tooltip="Display current RAM usage as %, bytes, or gigabytes",
            ),
        ]


class RamBar(AbstractComponent):
    TYPE_KEY = "ram_bar"
    DISPLAY_NAME = "RAM Bar"
    ICON_NAME = "ram_bar"
    DEFAULT_PROPERTIES = {"width": 0, "height": 0, "color": ""}

    # reference format (all args optional)
    # ${membar h,w}
    # ${color red}${membar h,w}${color}
    def render_conky_text(self, props: dict) -> str:
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color: str = props.get("color", "")

        var = "membar"
        if height != 0:
            var += f" {height}"
            if width != 0:
                var += f",{width}"

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
                tooltip="Bar width in pixels; 0 = use Conky's default bar width",
            ),
            PropertyField(
                key="height",
                label="height",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Bar height in pixels; 0 = use Conky's default bar height",
            ),
            PropertyField(
                key="color",
                label="Color",
                field_type="color",
                default="",
                tooltip="Leave empty to inherit the current Conky color",
            ),
        ]


class RamGraph(AbstractComponent):
    TYPE_KEY = "ram_graph"
    DISPLAY_NAME = "RAM Graph"
    ICON_NAME = "ram_graph"
    DEFAULT_PROPERTIES = {
        "width": 0,
        "height": 0,
        "color_lo": "",
        "color_hi": "",
    }

    # reference format (all args optional):
    # ${memgraph h,w color_lo color_hi}
    def render_conky_text(self, props: dict) -> str:
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color_lo: str = props.get("color_lo", "")
        color_hi: str = props.get("color_hi", "")

        var = "memgraph"
        if height != 0:
            var += f" {height}"
            if width != 0:
                var += f",{width}"
        if color_lo != "":
            var += f" {color_lo}"
        if color_hi != "":
            var += f" {color_hi}"
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
                tooltip="Graph width in pixels; 0 = use Conky's default graph width",
            ),
            PropertyField(
                key="height",
                label="height",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Graph height in pixels; 0 = use Conky's default graph height",
            ),
            PropertyField(
                key="color_lo",
                label="Color 1",
                field_type="color",
                default="",
                tooltip="Leave empty to inherit the current Conky color",
            ),
            PropertyField(
                key="color_hi",
                label="Color 2",
                field_type="color",
                default="",
                tooltip="Leave empty to inherit the current Conky color",
            ),
        ]


class SwapUsage(AbstractComponent):
    TYPE_KEY = "swap_usage"
    DISPLAY_NAME = "Swap Usage"
    ICON_NAME = "swap_usage"
    DEFAULT_PROPERTIES = {"format": "%"}

    # reference format (differs depending on choice)
    # ${swapperc} -- percentage
    # ${swap} -- GB used (human)
    # ${swapraw} -- bytes used
    def render_conky_text(self, props: dict) -> str:
        format: str = props.get("format", "%")

        if format == "human":
            return f"${{swap}}"
        elif format == "bytes":
            return f"${{swapraw}}"
        else:
            return f"${{swapperc}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="format",
                label="Format",
                field_type="choice",
                default="%",
                choices=["%", "bytes", "human"],
                tooltip="Display current Swap usage as %, bytes, or gigabytes",
            ),
        ]
