"""Tests for data models (Sub-Task 2)."""

import pytest

from gonky.models.settings import GlobalConkySettings
from gonky.models.component import ConkyComponent, COMPONENT_REGISTRY
from gonky.models.document import GonkyDocument, SchemaVersionError


# ---------------------------------------------------------------------------
# GlobalConkySettings
# ---------------------------------------------------------------------------

class TestGlobalConkySettings:
    def test_defaults(self):
        s = GlobalConkySettings()
        assert s.alignment == "top_left"
        assert s.gap_x == 10
        assert s.gap_y == 10
        assert s.window_width == 300
        assert s.window_height == 0
        assert s.own_window is True
        assert s.own_window_type == "desktop"
        assert s.own_window_transparent is True
        assert s.own_window_argb_visual is True
        assert s.double_buffer is True
        assert s.update_interval == 1.0
        assert s.default_font == "DejaVu Sans Mono"
        assert s.default_font_size == 10
        assert s.default_color == "white"
        assert s.background is False
        assert s.border_width == 0
        assert s.cpu_avg_samples == 2
        assert s.net_avg_samples == 2
        assert s.extra_lua == ""

    def test_custom_values(self):
        s = GlobalConkySettings(alignment="bottom_right", gap_x=5, update_interval=2.5)
        assert s.alignment == "bottom_right"
        assert s.gap_x == 5
        assert s.update_interval == 2.5


# ---------------------------------------------------------------------------
# ConkyComponent
# ---------------------------------------------------------------------------

class TestConkyComponent:
    def test_defaults(self):
        c = ConkyComponent()
        assert c.component_type == "text"
        assert c.label == "Text"
        assert c.canvas_x == 0
        assert c.canvas_y == 0
        assert c.enabled is True
        assert c.properties == {}

    def test_uuid_generated(self):
        c1 = ConkyComponent()
        c2 = ConkyComponent()
        assert c1.id != c2.id
        assert len(c1.id) == 36  # UUID4 canonical form

    def test_custom_values(self):
        c = ConkyComponent(
            id="fixed-id",
            component_type="cpu_bar",
            label="CPU",
            canvas_x=100,
            canvas_y=200,
            enabled=False,
            properties={"color": "red"},
        )
        assert c.id == "fixed-id"
        assert c.component_type == "cpu_bar"
        assert c.label == "CPU"
        assert c.canvas_x == 100
        assert c.canvas_y == 200
        assert c.enabled is False
        assert c.properties == {"color": "red"}

    def test_component_registry_is_dict(self):
        assert isinstance(COMPONENT_REGISTRY, dict)


# ---------------------------------------------------------------------------
# GonkyDocument — construction and defaults
# ---------------------------------------------------------------------------

class TestGonkyDocumentConstruction:
    def test_defaults(self):
        doc = GonkyDocument()
        assert doc.schema_version == "1.0"
        assert doc.project_name == "Untitled"
        assert isinstance(doc.settings, GlobalConkySettings)
        assert doc.components == []

    def test_settings_default_is_fresh_instance(self):
        doc1 = GonkyDocument()
        doc2 = GonkyDocument()
        # Each document must own its own settings object
        assert doc1.settings is not doc2.settings

    def test_components_default_is_fresh_list(self):
        doc1 = GonkyDocument()
        doc2 = GonkyDocument()
        doc1.components.append(ConkyComponent())
        assert doc2.components == []

    def test_custom_project_name(self):
        doc = GonkyDocument(project_name="My Conky")
        assert doc.project_name == "My Conky"


# ---------------------------------------------------------------------------
# GonkyDocument — to_dict / from_dict round-trip
# ---------------------------------------------------------------------------

class TestGonkyDocumentSerialization:
    def _make_doc(self):
        doc = GonkyDocument(project_name="Test Project")
        doc.settings.alignment = "bottom_left"
        doc.settings.update_interval = 2.0
        doc.components.append(
            ConkyComponent(
                id="comp-1",
                component_type="cpu_bar",
                label="CPU",
                canvas_x=10,
                canvas_y=20,
                enabled=True,
                properties={"width": 200},
            )
        )
        return doc

    def test_to_dict_returns_dict(self):
        doc = self._make_doc()
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_schema_version(self):
        d = GonkyDocument().to_dict()
        assert d["schema_version"] == "1.0"

    def test_to_dict_project_name(self):
        d = self._make_doc().to_dict()
        assert d["project_name"] == "Test Project"

    def test_to_dict_settings(self):
        d = self._make_doc().to_dict()
        assert d["settings"]["alignment"] == "bottom_left"
        assert d["settings"]["update_interval"] == 2.0

    def test_to_dict_components(self):
        d = self._make_doc().to_dict()
        assert len(d["components"]) == 1
        comp = d["components"][0]
        assert comp["id"] == "comp-1"
        assert comp["component_type"] == "cpu_bar"
        assert comp["properties"] == {"width": 200}

    def test_round_trip_empty_document(self):
        doc = GonkyDocument()
        restored = GonkyDocument.from_dict(doc.to_dict())
        assert restored.schema_version == doc.schema_version
        assert restored.project_name == doc.project_name
        assert restored.components == []

    def test_round_trip_with_components(self):
        doc = self._make_doc()
        restored = GonkyDocument.from_dict(doc.to_dict())
        assert restored.project_name == "Test Project"
        assert restored.settings.alignment == "bottom_left"
        assert restored.settings.update_interval == 2.0
        assert len(restored.components) == 1
        c = restored.components[0]
        assert c.id == "comp-1"
        assert c.component_type == "cpu_bar"
        assert c.label == "CPU"
        assert c.canvas_x == 10
        assert c.canvas_y == 20
        assert c.enabled is True
        assert c.properties == {"width": 200}

    def test_round_trip_multiple_components(self):
        doc = GonkyDocument(project_name="Multi")
        for i in range(3):
            doc.components.append(
                ConkyComponent(id=f"id-{i}", component_type="text", label=f"Label {i}")
            )
        restored = GonkyDocument.from_dict(doc.to_dict())
        assert len(restored.components) == 3
        assert restored.components[2].id == "id-2"

    def test_from_dict_missing_components_defaults_to_empty(self):
        data = {"schema_version": "1.0", "project_name": "No Comps"}
        doc = GonkyDocument.from_dict(data)
        assert doc.components == []

    def test_from_dict_missing_settings_defaults_to_defaults(self):
        data = {"schema_version": "1.0"}
        doc = GonkyDocument.from_dict(data)
        assert doc.settings.alignment == "top_left"


# ---------------------------------------------------------------------------
# GonkyDocument — SchemaVersionError
# ---------------------------------------------------------------------------

class TestSchemaVersionError:
    def test_raises_on_unknown_version(self):
        with pytest.raises(SchemaVersionError):
            GonkyDocument.from_dict({"schema_version": "99.0"})

    def test_raises_on_empty_version(self):
        with pytest.raises(SchemaVersionError):
            GonkyDocument.from_dict({"schema_version": ""})

    def test_raises_on_missing_version(self):
        with pytest.raises(SchemaVersionError):
            GonkyDocument.from_dict({"project_name": "No version key"})

    def test_error_message_contains_bad_version(self):
        with pytest.raises(SchemaVersionError, match="2.0"):
            GonkyDocument.from_dict({"schema_version": "2.0"})

    def test_valid_version_does_not_raise(self):
        doc = GonkyDocument.from_dict({"schema_version": "1.0"})
        assert doc.schema_version == "1.0"
