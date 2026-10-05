"""MainWindow — stub Gtk.ApplicationWindow for Sub-Task 1 scaffolding.

The full panel layout (toolbar, canvas, component library, properties panel,
statusbar) will be assembled in Sub-Task 4 (GUI Shell and Main Window Layout).
"""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402


class MainWindow(Gtk.ApplicationWindow):
    """Primary application window.

    Currently shows an empty window. Full layout to be implemented in Sub-Task 4.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.set_default_size(1024, 768)

        # Placeholder label shown until the real UI is assembled in Sub-Task 4.
        placeholder = Gtk.Label(label="Gonky — canvas coming soon (Sub-Task 4)")
        placeholder.set_vexpand(True)
        placeholder.set_hexpand(True)
        self.set_child(placeholder)
