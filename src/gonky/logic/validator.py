"""Validator — validates a GonkyDocument and returns structured error/warning list."""

import re
from dataclasses import dataclass
from typing import Literal

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

from gonky.models.component import COMPONENT_REGISTRY
from gonky.models.document import GonkyDocument

# Permissive Conky colour pattern:
#   #RGB, #RRGGBB, #RRGGBBAA  (hex)
#   0xRRGGBB                   (hex, Conky alternate)
#   word-only names             (e.g. "red", "white", "DarkSlateGray")
_COLOR_RE = re.compile(
    r"^(#[0-9a-fA-F]{3,8}|0x[0-9a-fA-F]{6}|[a-zA-Z]+)$"
)

# Named colours that Conky/X11 are known to accept — used only for warnings,
# not for blocking.  A non-exhaustive common subset is enough.
_KNOWN_NAMED_COLOURS = frozenset(
    {
        "aqua",
        "black",
        "blue",
        "cyan",
        "darkblue",
        "darkgreen",
        "darkred",
        "darkslategray",
        "darkslategrey",
        "fuchsia",
        "gray",
        "green",
        "grey",
        "lime",
        "magenta",
        "maroon",
        "navy",
        "olive",
        "orange",
        "purple",
        "red",
        "silver",
        "teal",
        "transparent",
        "white",
        "yellow",
    }
)


@dataclass
class ValidationError:
    """A single validation finding."""

    field: str
    component_id: str | None
    message: str
    severity: Literal["error", "warning"]


# ---------------------------------------------------------------------------
# Per-field validators
# ---------------------------------------------------------------------------


def validate_color(value: str) -> bool:
    """Return True when *value* is structurally valid as a Conky colour.

    Accepts ``#RGB``, ``#RRGGBB``, ``#RRGGBBAA``, ``0xRRGGBB``, and any
    alphabetic named colour string.  Returns False for structurally malformed
    strings such as ``#ZZZZZZ`` or ``"not valid 123"``.  Empty string is
    treated as "no override / inherit" and therefore considered valid.
    """
    if value == "":
        return True
    return bool(_COLOR_RE.match(value))


def validate_interval(value: float) -> bool:
    """Return True when *value* is a valid Conky update interval (>= 0.1 s)."""
    return value >= 0.1


def validate_font(value: str) -> bool:
    """Return True when *value* is a non-empty font name string."""
    return bool(value and value.strip())


def validate_mount_point(value: str) -> bool:
    """Return True when *value* looks like an absolute filesystem path."""
    return value.startswith("/")


def validate_network_interface(value: str) -> bool:
    """Return True when *value* is a non-empty string with no whitespace."""
    return bool(value) and not any(c.isspace() for c in value)


def validate_command(value: str) -> bool:
    """Return True when *value* is a non-empty string.

    No shell syntax validation is performed in v1.
    """
    return bool(value and value.strip())


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


class Validator:
    """Validates a :class:`~gonky.models.document.GonkyDocument`.

    Call :meth:`validate` to receive a list of
    :class:`ValidationError` instances — an empty list means the document is
    clean.  Errors with ``severity="error"`` block export/apply; warnings are
    advisory only.
    """

    def validate(self, doc: GonkyDocument) -> list[ValidationError]:
        """Validate *doc* and return all findings.

        Checks global settings first, then iterates enabled components.
        """
        errors: list[ValidationError] = []
        errors.extend(self._validate_settings(doc))
        errors.extend(self._validate_components(doc))
        return errors

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate_settings(self, doc: GonkyDocument) -> list[ValidationError]:
        s = doc.settings
        findings: list[ValidationError] = []

        if s.window_width < 0:
            findings.append(ValidationError(
                field="window_width",
                component_id=None,
                message=f"Window width must be >= 0, got {s.window_width}.",
                severity="error",
            ))

        if s.gap_x < 0:
            findings.append(ValidationError(
                field="gap_x",
                component_id=None,
                message=f"Gap X must be >= 0, got {s.gap_x}.",
                severity="error",
            ))

        if s.gap_y < 0:
            findings.append(ValidationError(
                field="gap_y",
                component_id=None,
                message=f"Gap Y must be >= 0, got {s.gap_y}.",
                severity="error",
            ))

        if not validate_interval(s.update_interval):
            findings.append(ValidationError(
                field="update_interval",
                component_id=None,
                message=f"Update interval must be >= 0.1, got {s.update_interval}.",
                severity="error",
            ))

        if not validate_font(s.default_font):
            findings.append(ValidationError(
                field="default_font",
                component_id=None,
                message="Default font must not be empty.",
                severity="error",
            ))

        if not validate_color(s.default_color):
            findings.append(ValidationError(
                field="default_color",
                component_id=None,
                message=f"Invalid colour value: {s.default_color!r}.",
                severity="error",
            ))

        return findings

    def _validate_components(self, doc: GonkyDocument) -> list[ValidationError]:
        findings: list[ValidationError] = []

        for component in doc.components:
            if not component.enabled:
                continue  # skip disabled components

            cid = component.id
            ctype = component.component_type

            if ctype not in COMPONENT_REGISTRY:
                findings.append(ValidationError(
                    field="component_type",
                    component_id=cid,
                    message=f"Unknown component type: {ctype!r}.",
                    severity="error",
                ))
                continue  # can't inspect schema for unknown type

            cls = COMPONENT_REGISTRY[ctype]
            props = {**cls.DEFAULT_PROPERTIES, **component.properties}
            schema = cls.property_schema()

            for field in schema:
                value = props.get(field.key)
                if value is None:
                    continue

                if field.field_type == "color":
                    self._check_color(field.key, str(value), cid, findings)
                elif field.key == "mount_point":
                    if not validate_mount_point(str(value)):
                        findings.append(ValidationError(
                            field=field.key,
                            component_id=cid,
                            message=f"Mount point must start with '/', got {value!r}.",
                            severity="error",
                        ))
                elif field.key == "interface":
                    if not validate_network_interface(str(value)):
                        findings.append(ValidationError(
                            field=field.key,
                            component_id=cid,
                            message=f"Network interface must be non-empty and have no spaces, got {value!r}.",
                            severity="error",
                        ))
                elif field.key == "command":
                    if not validate_command(str(value)):
                        findings.append(ValidationError(
                            field=field.key,
                            component_id=cid,
                            message="Command must not be empty.",
                            severity="error",
                        ))

        return findings

    def _check_color(
        self,
        field_key: str,
        value: str,
        component_id: str | None,
        findings: list[ValidationError],
    ) -> None:
        """Append colour findings to *findings* in-place."""
        if value == "":
            return  # empty means "inherit" — always valid

        if not validate_color(value):
            findings.append(ValidationError(
                field=field_key,
                component_id=component_id,
                message=f"Invalid colour value: {value!r}. "
                        "Expected #RGB, #RRGGBB, 0xRRGGBB, or a named colour.",
                severity="error",
            ))
            return

        # Alphabetic-only strings: warn when not a well-known named colour.
        if value.isalpha() and value.lower() not in _KNOWN_NAMED_COLOURS:
            findings.append(ValidationError(
                field=field_key,
                component_id=component_id,
                message=f"Colour name {value!r} is not a recognised X11/CSS name; "
                        "it may not render correctly in Conky.",
                severity="warning",
            ))
