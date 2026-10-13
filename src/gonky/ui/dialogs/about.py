"""About dialog — application information window."""

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gtk  # noqa: E402

from gonky.constants import APP_NAME, APP_VERSION


def show_about(parent: Gtk.Window) -> None:
    """Create and present the About dialog transient to *parent*."""
    dialog = Gtk.AboutDialog()
    dialog.set_transient_for(parent)
    dialog.set_modal(True)
    dialog.set_program_name(APP_NAME)
    dialog.set_version(APP_VERSION)
    dialog.set_comments("A graphical front-end for configuring Conky.")
    dialog.set_license_type(Gtk.License.GPL_3_0)
    dialog.set_website("https://github.com/gonky")
    dialog.set_website_label("GitHub")
    dialog.present()
