"""Validator — validates a GonkyDocument and returns a list of ValidationErrors."""

import re
from dataclasses import dataclass
from typing import Literal

from gonky.models.document import GonkyDocument


@dataclass
class ValidationError:
    """Represents a single validation finding.

    Attributes:
        field:        The field name that failed validation (e.g. ``"update_interval"``).
        component_id: The id of the component owning the field, or ``None`` for
                      global-settings errors.
        message:      Human-readable description of the problem.
        severity:     ``"error"`` blocks the action; ``"warning"`` lets the user
                      proceed after confirmation.
    """

    field: str
    component_id: str | None
    message: str
    severity: Literal["error", "warning"]


class Validator:
    """Validates a :class:`~gonky.models.document.GonkyDocument`.

    Call :meth:`validate` to get a list of :class:`ValidationError` objects.
    An empty list means the document is clean.
    """

    def validate(self, doc: GonkyDocument) -> list[ValidationError]:
        """Validate *doc* and return all findings.

        Global settings are checked first, then every component's properties.
        """
        errors: list[ValidationError] = []
        errors.extend(self._validate_settings(doc))
        errors.extend(self._validate_components(doc))
        return errors

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _validate_settings(self, doc: GonkyDocument) -> list[ValidationError]:
        """Validate :class:`~gonky.models.settings.GlobalConkySettings`."""
        errors: list[ValidationError] = []
        s = doc.settings

        if s.window_width < 0:
            errors.append(
                ValidationError(
                    field="window_width",
                    component_id=None,
                    message=f"Window width must be >= 0, got {s.window_width}.",
                    severity="error",
                )
            )

        if s.gap_x < 0:
            errors.append(
                ValidationError(
                    field="gap_x",
                    component_id=None,
                    message=f"Gap X must be >= 0, got {s.gap_x}.",
                    severity="error",
                )
            )

        if s.gap_y < 0:
            errors.append(
                ValidationError(
                    field="gap_y",
                    component_id=None,
                    message=f"Gap Y must be >= 0, got {s.gap_y}.",
                    severity="error",
                )
            )

        if not validate_interval(s.update_interval):
            errors.append(
                ValidationError(
                    field="update_interval",
                    component_id=None,
                    message=(
                        f"Update interval must be >= 0.1, got {s.update_interval}."
                    ),
                    severity="error",
                )
            )

        if not validate_font(s.default_font):
            errors.append(
                ValidationError(
                    field="default_font",
                    component_id=None,
                    message="Default font must not be empty.",
                    severity="error",
                )
            )

        if s.default_color and not validate_color(s.default_color):
            errors.append(
                ValidationError(
                    field="default_color",
                    component_id=None,
                    message=(
                        f"Default colour {s.default_color!r} is not a valid colour "
                        "string. Expected a hex value (#RRGGBB / #RGB / 0xRRGGBB) "
                        "or a named colour."
                    ),
                    severity="error",
                )
            )

        return errors

    def _validate_components(self, doc: GonkyDocument) -> list[ValidationError]:
        """Validate each component's properties using per-field rules."""
        import gonky.components  # noqa: F401 — populates COMPONENT_REGISTRY
        from gonky.models.component import COMPONENT_REGISTRY

        errors: list[ValidationError] = []

        for component in doc.components:
            cid = component.id
            ctype = component.component_type

            if ctype not in COMPONENT_REGISTRY:
                # Unknown types are a hard error — config gen would also fail.
                errors.append(
                    ValidationError(
                        field="component_type",
                        component_id=cid,
                        message=(
                            f"Unknown component type '{ctype}'. "
                            "This component will be skipped during export."
                        ),
                        severity="error",
                    )
                )
                continue

            cls = COMPONENT_REGISTRY[ctype]
            props = {**cls.DEFAULT_PROPERTIES, **component.properties}

            for field_def in cls.property_schema():
                value = props.get(field_def.key, field_def.default)
                field_errors = self._validate_field(field_def, value, cid)
                errors.extend(field_errors)

        return errors

    def _validate_field(
        self,
        field_def,
        value,
        component_id: str | None,
    ) -> list[ValidationError]:
        """Return validation errors for a single property field."""
        errors: list[ValidationError] = []
        key = field_def.key
        ftype = field_def.field_type

        if ftype == "color":
            # Empty string means "inherit" — skip validation.
            if isinstance(value, str) and value and not validate_color(value):
                errors.append(
                    ValidationError(
                        field=key,
                        component_id=component_id,
                        message=(
                            f"Field '{key}': {value!r} is not a valid colour string. "
                            "Expected a hex value (#RRGGBB / #RGB / 0xRRGGBB) "
                            "or a named colour."
                        ),
                        severity="error",
                    )
                )

        elif ftype == "text":
            # Apply semantic validators based on property key name.
            if key == "mount_point":
                if isinstance(value, str) and not validate_mount_point(value):
                    errors.append(
                        ValidationError(
                            field=key,
                            component_id=component_id,
                            message=(
                                f"Field '{key}': mount point must start with '/', "
                                f"got {value!r}."
                            ),
                            severity="error",
                        )
                    )
            elif key == "interface":
                if isinstance(value, str) and not validate_network_interface(value):
                    errors.append(
                        ValidationError(
                            field=key,
                            component_id=component_id,
                            message=(
                                f"Field '{key}': network interface must be a "
                                f"non-empty string with no whitespace, got {value!r}."
                            ),
                            severity="error",
                        )
                    )
            elif key == "command":
                if isinstance(value, str) and not validate_command(value):
                    errors.append(
                        ValidationError(
                            field=key,
                            component_id=component_id,
                            message=(
                                f"Field '{key}': command must not be empty."
                            ),
                            severity="error",
                        )
                    )

        elif ftype in ("int", "float"):
            # Honour min_val / max_val declared on the PropertyField.
            if field_def.min_val is not None and value < field_def.min_val:
                errors.append(
                    ValidationError(
                        field=key,
                        component_id=component_id,
                        message=(
                            f"Field '{key}': value {value} is below minimum "
                            f"{field_def.min_val}."
                        ),
                        severity="error",
                    )
                )
            if field_def.max_val is not None and value > field_def.max_val:
                errors.append(
                    ValidationError(
                        field=key,
                        component_id=component_id,
                        message=(
                            f"Field '{key}': value {value} exceeds maximum "
                            f"{field_def.max_val}."
                        ),
                        severity="error",
                    )
                )

        return errors


# ---------------------------------------------------------------------------
# Standalone field validator functions (used by the Validator and externally)
# ---------------------------------------------------------------------------

# Matches: #RGB, #RRGGBB, 0xRRGGBB, or a named colour (alphabetic-only string).
_COLOR_RE = re.compile(r"^(#[0-9a-fA-F]{3,6}|0x[0-9a-fA-F]{6}|[a-zA-Z]+)$")


def validate_color(value: str) -> bool:
    """Return ``True`` if *value* is a structurally valid Conky colour string.

    Accepts ``#RGB``, ``#RRGGBB``, ``0xRRGGBB``, and named colours (purely
    alphabetic strings such as ``"white"`` or ``"red"``).  Only structurally
    invalid strings (e.g. ``"#ZZZZZZ"`` or ``"not valid 123"``) return
    ``False``.
    """
    return bool(_COLOR_RE.match(value))


def validate_interval(value: float) -> bool:
    """Return ``True`` if *value* is a valid Conky update interval (>= 0.1)."""
    return value >= 0.1


def validate_font(value: str) -> bool:
    """Return ``True`` if *value* is a non-empty font name."""
    return bool(value)


def validate_mount_point(value: str) -> bool:
    """Return ``True`` if *value* is an absolute path (starts with ``/``)."""
    return value.startswith("/")


def validate_network_interface(value: str) -> bool:
    """Return ``True`` if *value* is a non-empty string with no whitespace."""
    return bool(value) and not any(c.isspace() for c in value)


def validate_command(value: str) -> bool:
    """Return ``True`` if *value* is a non-empty string (no deeper validation)."""
    return bool(value)
