"""Battery components."""

from gonky.components.base import AbstractComponent, PropertyField


class BatteryPercent(AbstractComponent):
    TYPE_KEY = "battery_percent"
    DISPLAY_NAME = "Battery %"
    ICON_NAME = "battery_percent"
    DEFAULT_PROPERTIES = {"battery_id": "BAT0"}

    # reference format:
    # ${battery_percent BAT0}
    def render_conky_text(self, props: dict) -> str:
        battery_id: str = props.get("battery_id", "BAT0")
        return f"${{battery_percent {battery_id}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="battery_id",
                label="Battery ID",
                field_type="text",
                default="BAT0",
                tooltip="Battery identifier as listed in /sys/class/power_supply/, e.g. BAT0 or BAT1",
            ),
        ]


class BatteryBar(AbstractComponent):
    TYPE_KEY = "battery_bar"
    DISPLAY_NAME = "Battery Bar"
    ICON_NAME = "battery_bar"
    DEFAULT_PROPERTIES = {"battery_id": "BAT0", "width": 0, "height": 0}

    # reference format (width and height are optional):
    # ${battery_bar h,w BAT0}
    def render_conky_text(self, props: dict) -> str:
        battery_id: str = props.get("battery_id", "BAT0")
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)

        var = "battery_bar"
        if height != 0:
            var += f" {height}"
            if width != 0:
                var += f",{width}"
        return f"${{{var} {battery_id}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="battery_id",
                label="Battery ID",
                field_type="text",
                default="BAT0",
                tooltip="Battery identifier as listed in /sys/class/power_supply/, e.g. BAT0 or BAT1",
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


class BatteryTime(AbstractComponent):
    TYPE_KEY = "battery_time"
    DISPLAY_NAME = "Battery Time Remaining"
    ICON_NAME = "battery_time"
    DEFAULT_PROPERTIES = {"battery_id": "BAT0"}

    # reference format:
    # ${battery_time BAT0}
    def render_conky_text(self, props: dict) -> str:
        battery_id: str = props.get("battery_id", "BAT0")
        return f"${{battery_time {battery_id}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="battery_id",
                label="Battery ID",
                field_type="text",
                default="BAT0",
                tooltip="Battery identifier as listed in /sys/class/power_supply/, e.g. BAT0 or BAT1",
            ),
        ]
