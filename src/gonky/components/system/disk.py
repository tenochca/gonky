"""Disk components."""

from gonky.components.base import AbstractComponent, PropertyField


class DiskUsage(AbstractComponent):
    TYPE_KEY = "disk_usage"
    DISPLAY_NAME = "Disk Usage"
    ICON_NAME = "disk_usage"
    DEFAULT_PROPERTIES = {"mount_point": "/", "format": "%"}

    # reference format:
    # ${fs_used mount_point}
    # ${fs_used_perc mount_point}
    def render_conky_text(self, props: dict) -> str:
        mount_point: str = props.get("mount_point", "/")
        format: str = props.get("format", "%")

        if format == "human":
            return f"${{fs_used {mount_point}}}"
        else:
            return f"${{fs_used_perc {mount_point}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="mount_point",
                label="Mount Point",
                field_type="text",
                default="/",
                tooltip="Point of origin for calculating usage",
            ),
            PropertyField(
                key="format",
                label="Format",
                field_type="choice",
                default="%",
                choices=["%", "human"],
                tooltip="Display current Disk usage as % or gigabytes",
            ),
        ]


class DiskBar(AbstractComponent):
    TYPE_KEY = "disk_bar"
    DISPLAY_NAME = "Disk Bar"
    ICON_NAME = "disk_bar"
    DEFAULT_PROPERTIES = {"mount_point": "/", "width": 0, "height": 0}

    # reference format (width and height are optional):
    # ${diskbar h,w mount_point}
    def render_conky_text(self, props: dict) -> str:
        mount_point: int = props.get("mount_point", 0)
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)

        var = "diskbar"
        if height != 0:
            var += f" {height}"
            if width != 0:
                var += f",{width}"
        return f"${{{var} {mount_point}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="mount_point",
                label="Mount Point",
                field_type="text",
                default="/",
                tooltip="Point of origin for calculating usage",
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
        ]


class DiskIO(AbstractComponent):
    TYPE_KEY = "disk_io"
    DISPLAY_NAME = "Disk I/O"
    ICON_NAME = "disk_io"
    DEFAULT_PROPERTIES = {"device": "", "direction": "total"}

    # reference format:
    # ${diskio device}
    # ${diskio_read device}
    # ${diskio_write device}
    def render_conky_text(self, props: dict) -> str:
        device: str = props.get("device", "")
        direction: str = props.get("direction", "total")

        if direction == "read":
            return f"${{diskio_read {device}}}"
        if direction == "write":
            return f"${{diskio_write {device}}}"
        else:
            return f"${{diskio {device}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="device",
                label="Device",
                field_type="text",
                default="",
                tooltip="Enter device name to capture it's speed",
            ),
            PropertyField(
                key="direction",
                label="Direction",
                field_type="choice",
                default="read",
                choices=["read", "write", "total"],
                tooltip="Display read or write speed",
            ),
        ]
