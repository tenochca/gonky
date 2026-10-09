"""Exec command component."""

from gonky.components.base import AbstractComponent, PropertyField


class ExecCommand(AbstractComponent):
    TYPE_KEY = "exec"
    DISPLAY_NAME = "Shell Command"
    ICON_NAME = "exec"
    DEFAULT_PROPERTIES = {
        "command": "",
        "exec_type": "exec",
    }

    # reference format:
    # ${exec command}
    # ${execbar command}
    # ${execgraph command}
    def render_conky_text(self, props: dict) -> str:
        command: str = props.get("command", "")
        exec_type: str = props.get("exec_type", "exec")

        if exec_type != "exec" and exec_type != "execbar" and exec_type != "execgraph":
            exec_type = "exec"

        return f"${{{exec_type} {command}}}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="command",
                label="Command",
                field_type="text",
                default="",
                tooltip="command to be ran",
            ),
            PropertyField(
                key="exec_type",
                label="Type",
                field_type="choice",
                default="exec",
                choices=["exec", "execbar", "execgraph"],
                tooltip="Select output format for command",
            ),
        ]
