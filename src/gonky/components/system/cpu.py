"""CPU components."""

from gonky.components.base import AbstractComponent, PropertyField


class CpuUsage(AbstractComponent):
    TYPE_KEY = "cpu_usage"
    DISPLAY_NAME = "CPU Usage %"
    ICON_NAME = "cpu_usage"
    DEFAULT_PROPERTIES = {"core": 0, "color": ""}

    # reference format (core num and color are both optional)
    # ${cpu cpu#}
    # ${color red}${cpubar cpu#}${color}
    def render_conky_text(self, props: dict) -> str:
        core: int = props.get("core", 0)
        color: str = props.get("color", "")

        if core == 0:
            var = "${cpu}"
        else:
            var = f"${{cpu cpu{core}}}"

        if color:
            return f"${{color {color}}}{var}${{color}}"
        return var

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="core",
                label="CPU Core",
                field_type="int",
                default=0,
                min_val=0,
                max_val=32,
                tooltip="0 = overall average; 1–N = individual core",
            ),
            PropertyField(
                key="color",
                label="Color",
                field_type="color",
                default="",
                tooltip="Leave empty to inherit the current Conky color",
            ),
        ]


class CpuBar(AbstractComponent):
    TYPE_KEY = "cpu_bar"
    DISPLAY_NAME = "CPU Bar"
    ICON_NAME = "cpu_bar"
    DEFAULT_PROPERTIES = {"core": 0, "width": 0, "height": 0, "color": ""}

    # reference format (all args are optional):
    # ${cpubar cpu# h,w}
    # ${color red}${cpubar cpu# h,w}${color}
    def render_conky_text(self, props: dict) -> str:
        core: int = props.get("core", 0)
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color: str = props.get("color", "")

        var = "cpubar"
        if core != 0:
            var += f" cpu{core}"
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
                key="core",
                label="CPU Core",
                field_type="int",
                default=0,
                min_val=0,
                max_val=32,
                tooltip="0 = overall average; 1–N = individual core",
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


class CpuGraph(AbstractComponent):
    TYPE_KEY = "cpu_graph"
    DISPLAY_NAME = "CPU Graph"
    ICON_NAME = "cpu_graph"
    DEFAULT_PROPERTIES = {
        "core": 0,
        "width": 0,
        "height": 0,
        "color_lo": "",
        "color_hi": "",
    }

    # reference format (all args are optional):
    # ${cpugraph cpu# h,w color_lo color_hi}
    def render_conky_text(self, props: dict) -> str:
        core: int = props.get("core", 0)
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color_lo: str = props.get("color_lo", "")
        color_hi: str = props.get("color_hi", "")

        var = "cpugraph"
        if core != 0:
            var += f" cpu{core}"
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
                key="core",
                label="CPU Core",
                field_type="int",
                default=0,
                min_val=0,
                max_val=32,
                tooltip="0 = overall average; 1–N = individual core",
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
                label="height",
                field_type="int",
                default=0,
                min_val=0,
                max_val=None,
                tooltip="Bar height in pixels; 0 = use Conky's default bar height",
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


class CpuFreq(AbstractComponent):
    TYPE_KEY = "cpu_freq"
    DISPLAY_NAME = "CPU Frequency"
    ICON_NAME = "cpu_freq"
    DEFAULT_PROPERTIES = {"core": 0}

    # reference format (core num is optional):
    # ${freq_g cpu#}
    def render_conky_text(self, props: dict) -> str:
        core: int = props.get("core", 0)

        return f"${{freq_g {core}}}"  # component only takes num, 0 is still average

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="core",
                label="CPU Core",
                field_type="int",
                default=0,
                min_val=0,
                max_val=32,
                tooltip="0 = overall average; 1–N = individual core",
            ),
        ]


class LoadAvg(AbstractComponent):
    TYPE_KEY = "load_avg"
    DISPLAY_NAME = "Load Average"
    ICON_NAME = "load_avg"
    DEFAULT_PROPERTIES = {"period": 0}

    # reference format (period optional, prints all 3):
    # ${loadavg period}
    def render_conky_text(self, props: dict) -> str:
        period: int = props.get("period", 0)

        # period ranges 0-3, 0 being default
        if period == 0:
            return "${{loadavg}}"
        return f"${{loadavg {period}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="period",
                label="Period (1, 5, 15)",
                field_type="int",
                default=0,
                min_val=0,
                max_val=3,
                tooltip="0 = all three intervals; 1–3 = respective interval in minutes",
            ),
        ]
