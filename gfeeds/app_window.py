from gettext import gettext as _
from gi.repository import Gtk, WebKit2
from .confManager import ConfManager
from .leaflet import GFeedsLeaflet
from .sidebar import GFeedsSidebar

from .download_manager import download
from .rss_parser import Feed

class GFeedsAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_title('GNOME Feeds')
        self.set_icon_name('org.gabmus.gnome-feeds')
        self.right_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        
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


        self.feeds = []
        self.feeds_items = []
        for f in self.confman.conf['feeds']:
            n_feed = Feed(download(f))
            self.feeds.append(n_feed)
            for i in n_feed.items:
                self.feeds_items.append(i)

        try: import operator; keyfun = operator.attrgetter('pub_date')
        except ImportError: keyfun = lambda x: x.pub_date
        
        self.feeds_items.sort(key=keyfun, reverse=True)

        self.sidebar = GFeedsSidebar()
        self.sidebar.listbox.connect('row-activated', self.on_sidebar_row_activated)

        self.webkitview = WebKit2.WebView()

        self.leaflet = GFeedsLeaflet()
        self.leaflet.add(self.sidebar)
        self.right_box.pack_start(self.webkitview, True, True, 0)
        self.leaflet.add(self.right_box)

        self.add(self.leaflet)

        self.sidebar.populate(self.feeds_items)
        

    def add_accelerator(self, shortcut, callback):
        if shortcut:
            key, mod = Gtk.accelerator_parse(shortcut)
            self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, callback)

    def emit_destroy(self, *args):
        self.emit('destroy')

    def on_destroy(self, *args):
        self.confman.save_conf()

    def on_sidebar_row_activated(self, listbox, row):
        self.webkitview.load_uri(row.feeditem.link)
