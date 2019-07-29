from gettext import gettext as _
from gi.repository import Gtk

class GFeedsOpmlFileChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, parent_window, **kwargs):
        super().__init__(
            _('Choose an OPML file to import'),
            parent_window,
            Gtk.FileChooserAction.OPEN,
            (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK
            )
        )
        self.filter = Gtk.FileFilter()
        self.filter.set_name('XML files')
        self.filter.add_mime_type('text/xml')
        self.add_filter(self.filter)
