from gi.repository import Gtk
from xml.sax.saxutils import escape
from gettext import gettext as _

class GFeedsConfirmAddDialog(Gtk.MessageDialog):
    def __init__(self, parent, f_path, **kwargs):
        super().__init__(
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            _('Do you want to import this file?'),
            **kwargs
        )

        self.format_secondary_markup(
            escape(f_path)
        )
