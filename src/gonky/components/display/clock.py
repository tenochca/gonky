"""Clock/date/uptime components."""

from gonky.components.base import AbstractComponent, PropertyField


class Clock(AbstractComponent):
    TYPE_KEY = "clock"
    DISPLAY_NAME = "Clock"
    ICON_NAME = "clock"
    DEFAULT_PROPERTIES = {"format": "%H:%M:%S"}

    # reference format:
    # ${time format}
    def render_conky_text(self, props: dict) -> str:
        format: str = props.get("format", "%H:%M:%S")

        return f"${{time {format}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="format",
                label="Clock format",
                field_type="text",
                default="%H:%M:%S",
                tooltip="strftime format string, e.g. %H:%M:%S for 14:05:30",
            ),
        ]


class Date(AbstractComponent):
    TYPE_KEY = "date"
    DISPLAY_NAME = "Date"
    ICON_NAME = "date"
    DEFAULT_PROPERTIES = {"format": "%Y-%m-%d"}

    # reference format:
    # ${time format}
    def render_conky_text(self, props: dict) -> str:
        format: str = props.get("format", "%Y-%m-%d")

        return f"${{time {format}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="format",
                label="Date format",
                field_type="text",
                default="%Y-%m-%d",
                tooltip="strftime format string, e.g. %Y-%m-%d for 2025-07-04",
            ),
        ]


class Uptime(AbstractComponent):
    TYPE_KEY = "uptime"
    DISPLAY_NAME = "Uptime"
    ICON_NAME = "uptime"
    DEFAULT_PROPERTIES = {}

    # reference format:
    # ${uptime}
    def render_conky_text(self, props: dict) -> str:
        return "${uptime}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return []
