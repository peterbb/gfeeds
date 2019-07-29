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
        self.add_filter(self.filter)\



class GFeedsOpmlSavePathChooserDialog(Gtk.FileChooserDialog):
    def __init__(self, parent_window, **kwargs):
        super().__init__(
            _('Choose where to save the exported OPML file'),
            parent_window,
            Gtk.FileChooserAction.SAVE,
            (
                Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK
            )
        )
        self.set_do_overwrite_confirmation(True)
        self.set_create_folders(True)
        self.filter = Gtk.FileFilter()
        self.filter.set_name('XML files')
        self.filter.add_mime_type('text/xml')
        self.add_filter(self.filter)
        self.set_current_name('GNOME-Feeds.opml')
