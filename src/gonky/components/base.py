"""AbstractComponent base class and PropertyField dataclass"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

@dataclass
class PropertyField:
    key: str
    label: str
    field_type: Literal["text", "int", "float", "bool", "color", "choice", "font"]
    default: Any
    choices: list[str] | None = None # used when field_type = "choice"
    min_val: float | None = None # used for int or float
    max_val: float | None = None # used for int or float
    tooltip: str = ""

class AbstractComponent(ABC):
    TYPE_KEY: str  # registry key (e.g cpu_bar) used in program
    DISPLAY_NAME: str # label seen by users
    ICON_NAME: str # filename in assets/icons/components/
    DEFAULT_PROPERTIES: dict # shallow copied per instantiation 

    @abstractmethod
    def render_conky_text(self, props: dict) -> str:
        """Return the conky.text fragment for this component instance."""
        pass

    @classmethod
    def property_schema(cls) -> list[PropertyField]:
        """Return the ordered PropertyField list (used by form_builder to 
        auto-generate the properties panel UI)"""
        return []
