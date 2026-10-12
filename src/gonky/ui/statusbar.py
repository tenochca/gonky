"""Status bar — stub for Sub-Task 4."""
# Implemented in Sub-Task 4 (GUI Shell and Main Window Layout).

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk

class StatusBar(Gtk.Box):
    """Horizontal bar at the bottom of the window.

    Left side  : scrollable message label for app notifications.
    Right side : coloured indicator showing whether Conky is running.
    """

    _MSG_DEFAULT = "Ready"
    _CONKY_RUNNING = "● Conky: running"
    _CONKY_STOPPED = "● Conky: stopped"


    def __init__(self) -> None:
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        self.add_css_class("statusbar")

        #left: message label
        self._message_label = Gtk.Label(label=self._MSG_DEFAULT)
        self._message_label.set_halign(Gtk.Align.START)
        self._message_label.set_hexpand(True)
        self._message_label.set_margin_start(8)
        self.append(self._message_label)