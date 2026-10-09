"""Temperature component."""

from gonky.components.base import AbstractComponent, PropertyField


class Temperature(AbstractComponent):
    TYPE_KEY = "temperature"
    DISPLAY_NAME = "Temperature"
    ICON_NAME = "temperature"
    DEFAULT_PROPERTIES = {
        "source": "hwmon",
        "hwmon_n": 0,
        "hwmon_type": 1,
        "hwmon_num": 1,
        "thermal_zone": 0,
        "unit": "C",
    }

    # reference formats:
    # hwmon:         ${hwmon N temp N}
    # thermal_zone:  ${acpitemp}  or  ${exec cat /sys/class/thermal/thermal_zoneN/temp}
    def render_conky_text(self, props: dict) -> str:
        source: str = props.get("source", "hwmon")
        unit: str = props.get("unit", "C")

        if source == "hwmon":
            hwmon_n: int = props.get("hwmon_n", 0)
            hwmon_type: int = props.get("hwmon_type", 1)
            hwmon_num: int = props.get("hwmon_num", 1)
            raw = f"${{hwmon {hwmon_n} temp {hwmon_num}}}"
        else:
            thermal_zone: int = props.get("thermal_zone", 0)
            raw = f"${{exec cat /sys/class/thermal/thermal_zone{thermal_zone}/temp}}"

        if unit == "F":
            # wrap in an exec awk expression to convert C→F at display time
            return f"${{exec echo $({raw}) | awk '{{printf \"%.0f\", $1 * 9/5 + 32}}'}}"
        return raw

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="source",
                label="Source",
                field_type="choice",
                default="hwmon",
                choices=["hwmon", "thermal_zone"],
                tooltip="hwmon = hardware monitor via ${hwmon}; thermal_zone = /sys/class/thermal/thermal_zoneN",
            ),
            PropertyField(
                key="hwmon_n",
                label="hwmon Index",
                field_type="int",
                default=0,
                min_val=0,
                max_val=16,
                tooltip="hwmon chip index (0-based), used when source=hwmon",
            ),
            PropertyField(
                key="hwmon_type",
                label="hwmon Type",
                field_type="int",
                default=1,
                min_val=1,
                max_val=16,
                tooltip="Sensor type number within the hwmon chip; 1 = first temp sensor",
            ),
            PropertyField(
                key="hwmon_num",
                label="hwmon Sensor Number",
                field_type="int",
                default=1,
                min_val=1,
                max_val=16,
                tooltip="Sensor index within the hwmon chip (1-based), used when source=hwmon",
            ),
            PropertyField(
                key="thermal_zone",
                label="Thermal Zone",
                field_type="int",
                default=0,
                min_val=0,
                max_val=16,
                tooltip="thermal_zone index (0-based), used when source=thermal_zone",
            ),
            PropertyField(
                key="unit",
                label="Unit",
                field_type="choice",
                default="C",
                choices=["C", "F"],
                tooltip="Temperature unit: C = Celsius; F = Fahrenheit",
            ),
        ]
