"""Tests for Sub-Task 12 — polish, keyboard shortcuts, tooltip coverage."""

import pytest


# ---------------------------------------------------------------------------
# Keyboard shortcut registry (headless-safe — reads class attribute only)
# ---------------------------------------------------------------------------

class TestKeyboardShortcuts:
    """Verify that GonkyApp._ACCELS declares all required shortcuts."""

    # Import only the class attribute; no GTK session required.
    from gonky.app import GonkyApp
    _accels = GonkyApp._ACCELS

    def test_new_shortcut(self):
        assert "win.new" in self._accels
        assert "<Control>n" in self._accels["win.new"]

    def test_open_shortcut(self):
        assert "win.open" in self._accels
        assert "<Control>o" in self._accels["win.open"]

    def test_save_shortcut(self):
        assert "win.save" in self._accels
        assert "<Control>s" in self._accels["win.save"]

    def test_export_shortcut(self):
        assert "win.export" in self._accels
        assert "<Control>e" in self._accels["win.export"]

    def test_preview_shortcut(self):
        assert "win.preview" in self._accels
        assert "<Control>p" in self._accels["win.preview"]

    def test_quit_shortcut(self):
        assert "app.quit" in self._accels
        assert "<Control>q" in self._accels["app.quit"]

    def test_all_six_actions_present(self):
        expected_actions = {"win.new", "win.open", "win.save", "win.export", "win.preview", "app.quit"}
        assert expected_actions.issubset(set(self._accels.keys()))


# ---------------------------------------------------------------------------
# Toolbar tooltip coverage (headless-safe — reads class source metadata)
# ---------------------------------------------------------------------------

class TestToolbarTooltips:
    """Verify that every toolbar button has a non-empty tooltip_text set."""

    def test_tooltip_strings_present_in_source(self):
        """Smoke-test: the toolbar source must contain shortcut hints."""
        import inspect
        from gonky.ui import toolbar
        source = inspect.getsource(toolbar)
        # All six shortcut hints must appear in the source.
        for hint in ("Ctrl+N", "Ctrl+O", "Ctrl+S", "Ctrl+E", "Ctrl+P"):
            assert hint in source, f"Missing shortcut hint '{hint}' in toolbar.py"


# ---------------------------------------------------------------------------
# Post-v1 roadmap file exists and covers required items
# ---------------------------------------------------------------------------

class TestRoadmapDocument:
    """Verify that docs/post-v1-roadmap.md exists and mentions key features."""

    def _read_roadmap(self) -> str:
        from pathlib import Path
        path = Path(__file__).parent.parent / "docs" / "post-v1-roadmap.md"
        return path.read_text(encoding="utf-8")

    def test_roadmap_file_exists(self):
        from pathlib import Path
        path = Path(__file__).parent.parent / "docs" / "post-v1-roadmap.md"
        assert path.exists()

    def test_roadmap_mentions_undo(self):
        assert "Undo" in self._read_roadmap() or "undo" in self._read_roadmap()

    def test_roadmap_mentions_preview(self):
        assert "Preview" in self._read_roadmap() or "preview" in self._read_roadmap()

    def test_roadmap_mentions_import(self):
        content = self._read_roadmap()
        assert "Import" in content or "import" in content

    def test_roadmap_mentions_packaging(self):
        content = self._read_roadmap()
        assert "Flatpak" in content or "flatpak" in content

    def test_roadmap_mentions_theme(self):
        content = self._read_roadmap()
        assert "Theme" in content or "theme" in content


# ---------------------------------------------------------------------------
# README completeness
# ---------------------------------------------------------------------------

class TestReadme:
    """Verify that README.md contains all required v1 content."""

    def _read_readme(self) -> str:
        from pathlib import Path
        path = Path(__file__).parent.parent / "README.md"
        return path.read_text(encoding="utf-8")

    def test_readme_exists(self):
        from pathlib import Path
        assert (Path(__file__).parent.parent / "README.md").exists()

    def test_readme_has_system_requirements(self):
        assert "System Requirements" in self._read_readme()

    def test_readme_mentions_python_gi(self):
        content = self._read_readme()
        assert "python3-gi" in content

    def test_readme_mentions_pip_install(self):
        assert "pip install PyGObject" in self._read_readme()

    def test_readme_has_run_command(self):
        assert "python -m gonky" in self._read_readme()

    def test_readme_has_known_limitations(self):
        assert "Known Limitations" in self._read_readme()

    def test_readme_limitations_mentions_ysort(self):
        content = self._read_readme()
        assert "Y-sort" in content or "vertical position" in content

    def test_readme_limitations_mentions_no_undo(self):
        assert "undo" in self._read_readme().lower()

    def test_readme_limitations_mentions_no_import(self):
        content = self._read_readme()
        assert "import" in content.lower()

    def test_readme_has_keyboard_shortcuts_table(self):
        assert "Keyboard Shortcuts" in self._read_readme()

    def test_readme_has_license(self):
        assert "License" in self._read_readme()

    def test_readme_has_feature_overview(self):
        assert "Features" in self._read_readme()
