"""GonkyDocument dataclass"""

import dataclasses
from dataclasses import dataclass, field

from gonky.models.settings import GlobalConkySettings
from gonky.models.component import ConkyComponent

SUPPORTED_VERSIONS = {"1.0"}

# Migration registry: maps schema_version string -> callable(dict) -> dict.
# A migration callable transforms a document dict from the given version to the
# next version.  Empty for v1 because "1.0" is the only existing version.
_MIGRATIONS: dict[str, callable] = {}


class SchemaVersionError(Exception):
    """Raised when a document's schema_version is not supported."""


@dataclass
class GonkyDocument:
    schema_version: str = "1.0"  # forward-compatibility hook
    project_name: str = "Untitled"
    settings: GlobalConkySettings = field(default_factory=GlobalConkySettings)
    components: list[ConkyComponent] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Serialise the document to a plain dict (JSON-safe)."""
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GonkyDocument":
        """Deserialise a document from a plain dict.

        Raises SchemaVersionError if the schema_version is not supported.
        Applies any registered migrations before constructing the object.
        """
        version = data.get("schema_version", "")
        if version not in SUPPORTED_VERSIONS:
            raise SchemaVersionError(
                f"Unsupported schema version: {version!r}. "
                f"Supported versions: {sorted(SUPPORTED_VERSIONS)}"
            )

        # Apply migrations in order if any are registered for this version.
        current = dict(data)
        if version in _MIGRATIONS:
            current = _MIGRATIONS[version](current)

        settings = GlobalConkySettings(**current.get("settings", {}))
        components = [
            ConkyComponent(**comp) for comp in current.get("components", [])
        ]
        return cls(
            schema_version=current.get("schema_version", "1.0"),
            project_name=current.get("project_name", "Untitled"),
            settings=settings,
            components=components,
        )
