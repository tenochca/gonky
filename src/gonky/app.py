"""GonkyApp — Gtk.Application subclass managing the application lifecycle."""

import atexit
import sys

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, Gdk  # noqa: E402

from gonky.constants import APP_ID, APP_CSS_PATH, APP_NAME, APP_ICON_PATH, ICONS_DIR
from gonky.ui.main_window import MainWindow


class GonkyApp(Gtk.Application):
    """Top-level GTK 4 application object.

    Responsibilities:
    - Register the application with the desktop session (single-instance).
    - Create and present the main window on activation.
    - Wire up global application actions (quit, new, open, save, export).
    - Register keyboard accelerators for all toolbar actions.
    """

    # Keyboard accelerator map: action name → accelerator string(s).
    _ACCELS: dict[str, list[str]] = {
        "win.new":     ["<Control>n"],
        "win.open":    ["<Control>o"],
        "win.save":    ["<Control>s"],
        "win.export":  ["<Control>e"],
        "win.preview": ["<Control>p"],
        "app.quit":    ["<Control>q"],
    }

    def __init__(self) -> None:
        super().__init__(
            application_id=APP_ID,
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
        )
        self.connect("activate", self._on_activate)
        self._register_app_actions()
        self._register_accels()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _register_app_actions(self) -> None:
        """Register application-level Gio.SimpleAction objects."""
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda _a, _p: self.quit())
        self.add_action(quit_action)

    def _register_accels(self) -> None:
        """Bind keyboard shortcuts to named actions."""
        for action_name, accels in self._ACCELS.items():
            self.set_accels_for_action(action_name, accels)

    def _on_activate(self, _app: Gtk.Application) -> None:
        """Called by GTK when the application is first started (or re-activated)."""
        self._load_css()
        self._register_icon_theme()
        window = MainWindow(application=self)
        window.set_title(APP_NAME)
        window.present()
        # Ensure the preview Conky process is killed when Python exits, even if
        # the window was closed without toggling the preview off first.
        atexit.register(window._preview_manager.stop_preview)

    def _load_css(self) -> None:
        """Load gonky.css into the default GTK display."""
        provider = Gtk.CssProvider()
        provider.load_from_path(str(APP_CSS_PATH))
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
        )

    def _register_icon_theme(self) -> None:
        """Add the assets/icons directory to the icon search path and set the app icon."""
        display = Gdk.Display.get_default()
        theme = Gtk.IconTheme.get_for_display(display)
        theme.add_search_path(str(ICONS_DIR))
        Gtk.Window.set_default_icon_name("gonky")

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def run(self) -> int:  # type: ignore[override]
        """Start the GTK main loop. Returns exit code."""
        return super().run(sys.argv)
