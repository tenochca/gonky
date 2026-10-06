"""ConkyComponent dataclass and COMPONENT_REGISTRY"""

from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class ConkyComponent:
    id: str = field(default_factory=lambda: str(uuid4()))
    component_type: str = "text" # placeholder values, lookup type
    label: str = "Text" 
    canvas_x: int = 0
    canvas_y: int = 0
    enabled: bool = True # skipped by config generator if false
    properties: dict = field(default_factory=dict)

# populated by components/__init__.py as concrete component classes are implemented
COMPONENT_REGISTRY: dict[str, type] = {
}



