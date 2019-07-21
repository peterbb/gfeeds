from gettext import gettext as _
from gi.repository import Gtk
from .confManager import ConfManager

class GFeedsAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_title('GNOME Feeds')
        self.set_icon_name('org.gabmus.gnome-feeds')
        self.container_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        
        # accel_group is for keyboard shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        shortcuts_l = [
            {
                'combo': '<Control>q',
                'cb': self.emit_destroy
            }
        ]
        for s in shortcuts_l:
            self.add_accelerator(s['combo'], s['cb'])

    def add_accelerator(self, shortcut, callback):
        if shortcut:
            key, mod = Gtk.accelerator_parse(shortcut)
            self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, callback)

    def emit_destroy(self, *args):
        self.emit('destroy')

    def on_destroy(self, *args):
        self.confman.save_conf()
