from gettext import gettext as _
from gi.repository import Gtk
from .confManager import ConfManager
from .leaflet import GFeedsLeaflet
from .sidebar import GFeedsSidebar
from .headerbar import GFeedHeaderbar
from .webview import GFeedsWebView

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

        try: import operator; self.keyfun = operator.attrgetter('pub_date')
        except ImportError: self.keyfun = lambda x: x.pub_date

        self.feeds = []
        self.feeds_items = []

        self.sidebar = GFeedsSidebar()
        self.sidebar.listbox.connect('row-activated', self.on_sidebar_row_activated)

        self.webview = GFeedsWebView()

        self.leaflet = GFeedsLeaflet()
        self.leaflet.add(self.sidebar)
        self.leaflet.add(self.webview)
        self.leaflet.connect('notify::folded', self.on_main_leaflet_folded)

        self.size_group_left = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.size_group_right = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.size_group_left.add_widget(self.sidebar)
        self.size_group_right.add_widget(self.webview)
        self.headerbar = GFeedHeaderbar(
            self.size_group_left,
            self.size_group_right,
            self.on_back_button_clicked,
            self.webview
        )
        self.headerbar.refresh_btn.connect('clicked', self.refresh_feeds)
        self.set_titlebar(self.headerbar)
        
        self.add(self.leaflet)

        self.refresh_feeds()
        

    def refresh_feeds(self, *args):
        self.feeds = []
        self.feeds_items = []
        for f in self.confman.conf['feeds']:
            n_feed = Feed(download(f))
            self.feeds.append(n_feed)
            for i in n_feed.items:
                self.feeds_items.append(i)

        self.feeds_items.sort(key=self.keyfun, reverse=True)
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
        self.webview.load_uri(row.feeditem.link)
        self.headerbar.open_externally_btn.set_sensitive(True)
        self.leaflet.set_visible_child(self.webview)
        self.headerbar.leaflet.set_visible_child(self.headerbar.right_headerbar)
        self.on_main_leaflet_folded()

    def on_main_leaflet_folded(self, *args):
        target = None
        # other = None
        if self.leaflet.folded:
            target = self.headerbar.leaflet.get_visible_child()
            self.headerbar.back_button.show()
        else:
            target = self.headerbar.right_headerbar
            self.headerbar.back_button.hide()
        # for c in self.headerbar.leaflet.get_children():
        #     if c != target:
        #         other = c
        #         break
        self.headerbar.headergroup.set_focus(target)
        # target.set_show_close_button(True)
        # other.set_show_close_button(False)

    def on_back_button_clicked(self, *args):
        self.leaflet.set_visible_child(self.sidebar)
        self.on_main_leaflet_folded()
