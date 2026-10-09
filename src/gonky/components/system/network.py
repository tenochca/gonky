"""Network components."""

from gonky.components.base import AbstractComponent, PropertyField


class NetUpload(AbstractComponent):
    TYPE_KEY = "net_upload"
    DISPLAY_NAME = "Net Upload Speed"
    ICON_NAME = "net_upload"
    DEFAULT_PROPERTIES = {"interface": "eth0"}

    # reference format:
    # ${upspeed interface}
    def render_conky_text(self, props: dict) -> str:
        interface: str = props.get("interface", "eth0")
        return f"${{upspeed {interface}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="interface",
                label="Interface",
                field_type="text",
                default="eth0",
                tooltip="Network interface name, e.g. eth0 or wlan0",
            ),
        ]


class NetDownload(AbstractComponent):
    TYPE_KEY = "net_download"
    DISPLAY_NAME = "Net Download Speed"
    ICON_NAME = "net_download"
    DEFAULT_PROPERTIES = {"interface": "eth0"}

    # reference format:
    # ${downspeed interface}
    def render_conky_text(self, props: dict) -> str:
        interface: str = props.get("interface", "eth0")
        return f"${{downspeed {interface}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="interface",
                label="Interface",
                field_type="text",
                default="eth0",
                tooltip="Network interface name, e.g. eth0 or wlan0",
            ),
        ]


class NetUploadGraph(AbstractComponent):
    TYPE_KEY = "net_upload_graph"
    DISPLAY_NAME = "Net Upload Graph"
    ICON_NAME = "net_upload_graph"
    DEFAULT_PROPERTIES = {
        "interface": "eth0",
        "width": 0,
        "height": 0,
        "color_lo": "",
        "color_hi": "",
    }

    # reference format (all args optional except interface):
    # ${upspeedgraph interface h,w color_lo color_hi}
    def render_conky_text(self, props: dict) -> str:
        interface: str = props.get("interface", "eth0")
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color_lo: str = props.get("color_lo", "")
        color_hi: str = props.get("color_hi", "")

        var = f"upspeedgraph {interface}"
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
                key="interface",
                label="Interface",
                field_type="text",
                default="eth0",
                tooltip="Network interface name, e.g. eth0 or wlan0",
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
                tooltip="Graph color at low speed; both colors must be set together",
            ),
            PropertyField(
                key="color_hi",
                label="Color High",
                field_type="color",
                default="",
                tooltip="Graph color at high speed; both colors must be set together",
            ),
        ]


class NetDownloadGraph(AbstractComponent):
    TYPE_KEY = "net_download_graph"
    DISPLAY_NAME = "Net Download Graph"
    ICON_NAME = "net_download_graph"
    DEFAULT_PROPERTIES = {
        "interface": "eth0",
        "width": 0,
        "height": 0,
        "color_lo": "",
        "color_hi": "",
    }

    # reference format (all args optional except interface):
    # ${downspeedgraph interface h,w color_lo color_hi}
    def render_conky_text(self, props: dict) -> str:
        interface: str = props.get("interface", "eth0")
        width: int = props.get("width", 0)
        height: int = props.get("height", 0)
        color_lo: str = props.get("color_lo", "")
        color_hi: str = props.get("color_hi", "")

        var = f"downspeedgraph {interface}"
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
                key="interface",
                label="Interface",
                field_type="text",
                default="eth0",
                tooltip="Network interface name, e.g. eth0 or wlan0",
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
                tooltip="Graph color at low speed; both colors must be set together",
            ),
            PropertyField(
                key="color_hi",
                label="Color High",
                field_type="color",
                default="",
                tooltip="Graph color at high speed; both colors must be set together",
            ),
        ]


class NetIp(AbstractComponent):
    TYPE_KEY = "net_ip"
    DISPLAY_NAME = "IP Address"
    ICON_NAME = "net_ip"
    DEFAULT_PROPERTIES = {"interface": "eth0"}

    # reference format:
    # ${addr interface}
    def render_conky_text(self, props: dict) -> str:
        interface: str = props.get("interface", "eth0")
        return f"${{addr {interface}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="interface",
                label="Interface",
                field_type="text",
                default="eth0",
                tooltip="Network interface name, e.g. eth0 or wlan0",
            ),
        ]
