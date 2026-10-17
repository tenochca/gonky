"""Tests for the file manager — save, load, and export (Sub-Task 11)."""

import json

import pytest

import gonky.components  # noqa: F401 — side-effect: populates COMPONENT_REGISTRY

from gonky.logic.file_manager import (
    export_config,
    get_default_export_path,
    load_project,
    save_project,
)
from gonky.models.component import ConkyComponent
from gonky.models.document import GonkyDocument, SchemaVersionError
from gonky.models.settings import GlobalConkySettings


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_doc(project_name: str = "Test") -> GonkyDocument:
    """Return a document with one CPU-bar component and custom settings."""
    doc = GonkyDocument(project_name=project_name)
    doc.settings.alignment = "bottom_right"
    doc.settings.update_interval = 2.0
    doc.components.append(
        ConkyComponent(
            id="comp-abc",
            component_type="cpu_bar",
            label="CPU",
            canvas_x=10,
            canvas_y=20,
            enabled=True,
            properties={"height": 8, "width": 150},
        )
    )
    return doc


# ---------------------------------------------------------------------------
# save_project
# ---------------------------------------------------------------------------


class TestSaveProject:
    def test_creates_file_with_gonky_extension(self, tmp_path):
        path = tmp_path / "myproject"
        save_project(GonkyDocument(), path)
        assert (tmp_path / "myproject.gonky").exists()

    def test_written_file_is_valid_json(self, tmp_path):
        path = tmp_path / "p"
        save_project(GonkyDocument(), path)
        content = (tmp_path / "p.gonky").read_text(encoding="utf-8")
        parsed = json.loads(content)
        assert isinstance(parsed, dict)

    def test_written_file_contains_schema_version(self, tmp_path):
        save_project(GonkyDocument(), tmp_path / "d")
        data = json.loads((tmp_path / "d.gonky").read_text())
        assert data["schema_version"] == "1.0"

    def test_written_file_contains_project_name(self, tmp_path):
        doc = GonkyDocument(project_name="My Widget")
        save_project(doc, tmp_path / "p")
        data = json.loads((tmp_path / "p.gonky").read_text())
        assert data["project_name"] == "My Widget"

    def test_written_file_contains_components(self, tmp_path):
        doc = make_doc()
        save_project(doc, tmp_path / "p")
        data = json.loads((tmp_path / "p.gonky").read_text())
        assert len(data["components"]) == 1
        assert data["components"][0]["id"] == "comp-abc"

    def test_creates_missing_parent_directories(self, tmp_path):
        deep_path = tmp_path / "a" / "b" / "c" / "project"
        save_project(GonkyDocument(), deep_path)
        assert (tmp_path / "a" / "b" / "c" / "project.gonky").exists()

    def test_overwrites_existing_file(self, tmp_path):
        path = tmp_path / "p"
        save_project(GonkyDocument(project_name="First"), path)
        save_project(GonkyDocument(project_name="Second"), path)
        data = json.loads((tmp_path / "p.gonky").read_text())
        assert data["project_name"] == "Second"

    def test_already_has_gonky_extension_not_doubled(self, tmp_path):
        """Passing a path that already ends in .gonky should not produce .gonky.gonky."""
        path = tmp_path / "project.gonky"
        save_project(GonkyDocument(), path)
        assert (tmp_path / "project.gonky").exists()
        assert not (tmp_path / "project.gonky.gonky").exists()


# ---------------------------------------------------------------------------
# load_project
# ---------------------------------------------------------------------------


class TestLoadProject:
    def test_load_returns_gonky_document(self, tmp_path):
        path = tmp_path / "p"
        save_project(GonkyDocument(), path)
        doc = load_project(tmp_path / "p.gonky")
        assert isinstance(doc, GonkyDocument)

    def test_load_raises_file_not_found(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_project(tmp_path / "nonexistent.gonky")

    def test_load_raises_json_decode_error_on_bad_content(self, tmp_path):
        bad_file = tmp_path / "bad.gonky"
        bad_file.write_text("this is not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            load_project(bad_file)

    def test_load_raises_schema_version_error(self, tmp_path):
        bad_file = tmp_path / "future.gonky"
        bad_file.write_text(
            json.dumps({"schema_version": "99.0", "project_name": "X"}),
            encoding="utf-8",
        )
        with pytest.raises(SchemaVersionError):
            load_project(bad_file)


# ---------------------------------------------------------------------------
# save + load round-trip
# ---------------------------------------------------------------------------


class TestSaveLoadRoundTrip:
    def test_empty_document_round_trip(self, tmp_path):
        doc = GonkyDocument()
        path = tmp_path / "doc"
        save_project(doc, path)
        restored = load_project(tmp_path / "doc.gonky")
        assert restored.schema_version == doc.schema_version
        assert restored.project_name == doc.project_name
        assert restored.components == []

    def test_round_trip_preserves_project_name(self, tmp_path):
        doc = GonkyDocument(project_name="Preserved Name")
        path = tmp_path / "p"
        save_project(doc, path)
        assert load_project(tmp_path / "p.gonky").project_name == "Preserved Name"

    def test_round_trip_preserves_settings(self, tmp_path):
        doc = GonkyDocument()
        doc.settings.alignment = "bottom_left"
        doc.settings.update_interval = 3.0
        doc.settings.default_color = "#ff8800"
        path = tmp_path / "s"
        save_project(doc, path)
        restored = load_project(tmp_path / "s.gonky")
        assert restored.settings.alignment == "bottom_left"
        assert restored.settings.update_interval == 3.0
        assert restored.settings.default_color == "#ff8800"

    def test_round_trip_preserves_single_component(self, tmp_path):
        doc = make_doc()
        path = tmp_path / "c"
        save_project(doc, path)
        restored = load_project(tmp_path / "c.gonky")
        assert len(restored.components) == 1
        c = restored.components[0]
        assert c.id == "comp-abc"
        assert c.component_type == "cpu_bar"
        assert c.label == "CPU"
        assert c.canvas_x == 10
        assert c.canvas_y == 20
        assert c.enabled is True
        assert c.properties == {"height": 8, "width": 150}

    def test_round_trip_preserves_multiple_components(self, tmp_path):
        doc = GonkyDocument(project_name="Multi")
        types = ["cpu_usage", "ram_usage", "separator", "clock", "text"]
        for i, t in enumerate(types):
            doc.components.append(
                ConkyComponent(id=f"id-{i}", component_type=t, canvas_y=i * 10)
            )
        path = tmp_path / "m"
        save_project(doc, path)
        restored = load_project(tmp_path / "m.gonky")
        assert len(restored.components) == 5
        for i, (c, t) in enumerate(zip(restored.components, types)):
            assert c.id == f"id-{i}"
            assert c.component_type == t

    def test_round_trip_disabled_component(self, tmp_path):
        doc = GonkyDocument()
        doc.components.append(
            ConkyComponent(id="off-id", component_type="cpu_usage", enabled=False)
        )
        path = tmp_path / "disabled"
        save_project(doc, path)
        restored = load_project(tmp_path / "disabled.gonky")
        assert restored.components[0].enabled is False

    def test_round_trip_settings_default_is_correct(self, tmp_path):
        """Loading a file with minimal settings data produces correct defaults."""
        data = {"schema_version": "1.0", "project_name": "Minimal"}
        minimal_file = tmp_path / "minimal.gonky"
        minimal_file.write_text(json.dumps(data), encoding="utf-8")
        doc = load_project(minimal_file)
        assert doc.settings.alignment == "top_left"
        assert doc.settings.update_interval == 1.0


# ---------------------------------------------------------------------------
# export_config
# ---------------------------------------------------------------------------


class TestExportConfig:
    def test_creates_conf_file(self, tmp_path):
        path = tmp_path / "conky.conf"
        export_config(GonkyDocument(), path)
        assert path.exists()

    def test_exported_file_contains_config_block(self, tmp_path):
        path = tmp_path / "out.conf"
        export_config(GonkyDocument(), path)
        content = path.read_text(encoding="utf-8")
        assert "conky.config = {" in content

    def test_exported_file_contains_text_block(self, tmp_path):
        path = tmp_path / "out.conf"
        export_config(GonkyDocument(), path)
        content = path.read_text(encoding="utf-8")
        assert "conky.text = [[" in content
        assert "]]" in content

    def test_creates_missing_parent_directories(self, tmp_path):
        deep_path = tmp_path / "x" / "y" / "z" / "conky.conf"
        export_config(GonkyDocument(), deep_path)
        assert deep_path.exists()

    def test_exported_config_reflects_settings(self, tmp_path):
        doc = GonkyDocument()
        doc.settings.default_font = "Noto Mono"
        doc.settings.default_font_size = 12
        path = tmp_path / "styled.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert "font = 'Noto Mono:size=12'" in content

    def test_exported_config_contains_component_output(self, tmp_path):
        doc = GonkyDocument()
        doc.components.append(
            ConkyComponent(component_type="separator", canvas_y=0)
        )
        path = tmp_path / "with_sep.conf"
        export_config(doc, path)
        content = path.read_text(encoding="utf-8")
        assert "${hr}" in content

    def test_export_overwrites_existing_file(self, tmp_path):
        path = tmp_path / "conky.conf"
        path.write_text("old content", encoding="utf-8")
        export_config(GonkyDocument(), path)
        content = path.read_text(encoding="utf-8")
        assert "conky.config" in content
        assert "old content" not in content


# ---------------------------------------------------------------------------
# get_default_export_path
# ---------------------------------------------------------------------------


class TestGetDefaultExportPath:
    def test_returns_path_object(self):
        from pathlib import Path
        assert isinstance(get_default_export_path(), Path)

    def test_ends_with_conky_conf(self):
        p = get_default_export_path()
        assert p.name == "conky.conf"

    def test_under_config_conky_directory(self):
        p = get_default_export_path()
        assert p.parent.name == "conky"
        assert p.parent.parent.name == ".config"
