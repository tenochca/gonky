"""Process components."""

from gonky.components.base import AbstractComponent, PropertyField


class Processes(AbstractComponent):
    TYPE_KEY = "processes"
    DISPLAY_NAME = "Top Processes"
    ICON_NAME = "processes"
    DEFAULT_PROPERTIES = {"count": 5, "sort_by": "cpu"}

    # reference format:
    # ${top name N}${top cpu N}     -- CPU-sorted
    # ${top_mem name N}${top_mem mem N} -- memory-sorted
    # Each row: name + value on one line
    def render_conky_text(self, props: dict) -> str:
        count: int = props.get("count", 5)
        sort_by: str = props.get("sort_by", "cpu")

        if count < 1:
            count = 1

        prefix = "top" if sort_by == "cpu" else "top_mem"
        lines = []
        for i in range(1, count + 1):
            lines.append(f"${{{prefix} name {i}}} ${{{prefix} {sort_by} {i}}}")
        return "\n".join(lines)

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="count",
                label="Count",
                field_type="int",
                default=5,
                min_val=1,
                max_val=20,
                tooltip="Number of processes to list",
            ),
            PropertyField(
                key="sort_by",
                label="Sort By",
                field_type="choice",
                default="cpu",
                choices=["cpu", "mem"],
                tooltip="cpu = sort by CPU usage; mem = sort by memory usage",
            ),
        ]


class ProcessCount(AbstractComponent):
    TYPE_KEY = "process_count"
    DISPLAY_NAME = "Process Count"
    ICON_NAME = "process_count"
    DEFAULT_PROPERTIES = {"count_type": "running"}

    # reference format:
    # ${running_processes}  -- currently running processes
    # ${processes}          -- total processes
    def render_conky_text(self, props: dict) -> str:
        count_type: str = props.get("count_type", "running")

        if count_type == "total":
            return "${processes}"
        return "${running_processes}"

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        return [
            PropertyField(
                key="count_type",
                label="Count Type",
                field_type="choice",
                default="running",
                choices=["running", "total"],
                tooltip="running = currently running processes; total = all processes including sleeping",
            ),
        ]
