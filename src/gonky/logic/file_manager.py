"""File manager — save, load, and export Gonky project files."""

import json
from pathlib import Path

from gonky.logic.config_generator import ConfigGenerator
from gonky.models.document import GonkyDocument, SchemaVersionError


def save_project(doc: GonkyDocument, path: Path) -> None:
    """Write *doc* to *path* as a JSON file with a `.gonky` extension.

    The file is created (and its parent directories) if they do not exist.
    """
    target = path.with_suffix(".gonky")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(doc.to_dict(), indent=2), encoding="utf-8")


def load_project(path: Path) -> GonkyDocument:
    """Read a `.gonky` JSON file and return a ``GonkyDocument``.

    Raises:
        SchemaVersionError: if the file's schema_version is not supported.
        FileNotFoundError: if *path* does not exist.
        json.JSONDecodeError: if the file is not valid JSON.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return GonkyDocument.from_dict(data)


def export_config(doc: GonkyDocument, path: Path) -> None:
    """Generate a Conky config string from *doc* and write it to *path*.

    Parent directories are created automatically if they do not exist.
    """
    config_text = ConfigGenerator().generate(doc)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(config_text, encoding="utf-8")


def get_default_export_path() -> Path:
    """Return ``~/.config/conky/conky.conf`` as the default export location."""
    return Path.home() / ".config" / "conky" / "conky.conf"
