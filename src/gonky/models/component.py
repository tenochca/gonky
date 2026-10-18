"""ConkyComponent dataclass and COMPONENT_REGISTRY"""

from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class ConkyComponent:
    id: str = field(default_factory=lambda: str(uuid4()))
    component_type: str = "text" # placeholder values, lookup type
    label: str = ""        # user-editable prefix emitted verbatim before the component value in config output; "" = no prefix
    label_color: str = ""  # Conky color applied to the label prefix only; "" = inherit current color
    canvas_x: int = 0
    canvas_y: int = 0
    enabled: bool = True   # skipped by config generator if false
    no_newline: bool = False  # when True, the generator omits the trailing \n so the next component shares the same line
    properties: dict = field(default_factory=dict)

# populated by components/__init__.py as concrete component classes are implemented
COMPONENT_REGISTRY: dict[str, type] = {
}



