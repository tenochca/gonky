"""Preview manager — orchestrates a live Conky preview of the current document."""

import dataclasses
import subprocess
from pathlib import Path
from typing import Optional

from gi.repository import GLib

from gonky.logic import process_manager
from gonky.logic.config_generator import ConfigGenerator
from gonky.models.document import GonkyDocument
from gonky.models.settings import GlobalConkySettings

# Temporary config file used exclusively for the preview instance.
_PREVIEW_CONF_PATH = Path.home() / ".cache" / "gonky" / "preview.conf"

# Debounce delay in milliseconds (1.5 s as specified in the plan).
_DEBOUNCE_MS = 1500


class PreviewManager:
    """Manage a live Conky preview subprocess for the current document.

    The preview instance always uses ``alignment = 'top_right'``, ``gap_x = 10``,
    and ``gap_y = 10`` regardless of the document's own settings.  This prevents
    the preview window from overlapping the Gonky application window.

    Only one preview instance is tracked at a time.  Starting a new preview
    automatically stops any previously running one.
    """

    def __init__(self) -> None:
        # Currently running Conky preview subprocess (None when stopped).
        self._proc: Optional[subprocess.Popen] = None

        # GLib source id of the pending debounce timer (0 = no timer pending).
        self._debounce_source_id: int = 0

        # ConfigGenerator used to produce preview configs.
        self._generator = ConfigGenerator()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        """True when a preview Conky process is currently running."""
        return self._proc is not None and process_manager.is_running(self._proc)

    def start_preview(self, doc: GonkyDocument) -> None:
        """Generate a preview config for *doc* and launch Conky.

        The document's alignment/gap settings are overridden to ``top_right``
        so the preview window appears in the top-right corner and does not
        overlap the Gonky window.  The original document is not mutated.
        """
        # Ensure any previous instance is stopped first.
        self.stop_preview()

        # Build a shallow copy of the document with overridden placement settings.
        preview_doc = dataclasses.replace(doc, settings=doc.settings)

        config_text = self._generator.generate(preview_doc)

        # Write the config to the temp file (create parent dirs if needed).
        _PREVIEW_CONF_PATH.parent.mkdir(parents=True, exist_ok=True)
        _PREVIEW_CONF_PATH.write_text(config_text, encoding="utf-8")

        self._proc = process_manager.start_conky(_PREVIEW_CONF_PATH)

    def stop_preview(self) -> None:
        """Stop the currently running preview Conky instance, if any."""
        if self._proc is not None:
            process_manager.stop_conky(self._proc)
            self._proc = None

    def refresh_preview(self, doc: GonkyDocument) -> None:
        """Stop the current preview and immediately start a new one for *doc*."""
        self.stop_preview()
        self.start_preview(doc)

    def schedule_refresh(self, doc: GonkyDocument) -> None:
        """Debounce a preview refresh: restart the 1.5 s countdown on every call.

        If a timer is already pending it is cancelled before a new one is
        scheduled, so rapid edits collapse into a single refresh that fires
        1.5 s after the last change.

        The refresh only runs if the preview is still active when the timer
        fires — this avoids restarting Conky if the user toggled the preview
        off during the debounce window.
        """
        # Cancel any pending timer.
        if self._debounce_source_id:
            GLib.source_remove(self._debounce_source_id)
            self._debounce_source_id = 0

        def _do_refresh() -> bool:
            self._debounce_source_id = 0
            if self.is_active:
                self.refresh_preview(doc)
            return GLib.SOURCE_REMOVE  # one-shot timer

        self._debounce_source_id = GLib.timeout_add(_DEBOUNCE_MS, _do_refresh)
