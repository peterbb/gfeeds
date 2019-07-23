from gettext import gettext as _
from gi.repository import Gtk, WebKit2
from .confManager import ConfManager
from .leaflet import GFeedsLeaflet
from .sidebar import GFeedsSidebar
from .headerbar import GFeedHeaderbar

from .download_manager import download
from .rss_parser import Feed

class GFeedsAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_title('GNOME Feeds')
        self.set_icon_name('org.gabmus.gnome-feeds')
        
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
        self.webkitview.set_hexpand(True)
        self.webkitview.set_size_request(300, 500)

        self.leaflet = GFeedsLeaflet()
        self.leaflet.add(self.sidebar)
        self.leaflet.add(self.webkitview)
        self.leaflet.connect('notify::folded', self.on_main_leaflet_folded)

        self.size_group_left = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.size_group_right = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.size_group_left.add_widget(self.sidebar)
        self.size_group_right.add_widget(self.webkitview)
        self.headerbar = GFeedHeaderbar(self.size_group_left, self.size_group_right)
        self.set_titlebar(self.headerbar)
        

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

    def on_main_leaflet_folded(self, *args):
        target = None
        # other = None
        if self.leaflet.folded:
            target = self.headerbar.left_headerbar if self.leaflet.get_visible_child() == self.sidebar else self.headerbar.right_headerbar
        else:
            target = self.headerbar.right_headerbar
        # for c in self.headerbar.leaflet.get_children():
        #     if c != target:
        #         other = c
        #         break
        self.headerbar.headergroup.set_focus(target)
        # target.set_show_close_button(True)
        # other.set_show_close_button(False)
