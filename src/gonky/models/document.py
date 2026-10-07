"""GonkyDocument dataclass"""

from dataclasses import dataclass, field

from gonky.models.settings import GlobalConkySettings
from gonky.models.component import ConkyComponent

@dataclass
class GonkyDocument:
    schema_version: str = "1.0"  # forward-compatibility hook
    project_name: str = "Untitled"
    settings: GlobalConkySettings = field(default_factory=GlobalConkySettings)
    components: list[ConkyComponent] = field(default_factory=list)
