from gettext import gettext as _
from gi.repository import Gtk, GLib, Handy
import threading
from .confManager import ConfManager
from .feeds_manager import FeedsManager
from .leaflet import GFeedsLeaflet
from .sidebar import GFeedsSidebar
from .headerbar import GFeedHeaderbar
from .suggestion_bar import (
    GFeedsConnectionBar,
    GFeedsSuggestionBar,
    GFeedsErrorsBar
)
from .webview import GFeedsWebView
from .rss_parser import Feed

class GFeedsAppWindow(Gtk.ApplicationWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.feedman = FeedsManager()

        self.set_title('Feeds')
        self.set_icon_name('org.gabmus.gfeeds')

        self.sidebar = GFeedsSidebar()
        self.sidebar.listbox.connect(
            'row-activated',
            self.on_sidebar_row_activated
        )
        self.sidebar.saved_items_listbox.connect(
            'row-activated',
            self.on_sidebar_row_activated
        )

        self.webview = GFeedsWebView()

        separator = Gtk.Separator()
        separator.get_style_context().add_class('sidebar')

        self.leaflet = GFeedsLeaflet()
        self.suggestion_bar = GFeedsSuggestionBar()
        self.connection_bar = GFeedsConnectionBar()
        self.errors_bar = GFeedsErrorsBar(self)
        self.feedman.connect(
            'feedmanager_refresh_end',
            lambda *args: self.errors_bar.engage(self.feedman.errors)
        )
        self.sidebar_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.sidebar_box.pack_start(self.suggestion_bar, False, False, 0)
        self.sidebar_box.pack_start(self.connection_bar, False, False, 0)
        self.sidebar_box.pack_start(self.errors_bar, False, False, 0)
        self.sidebar_box.pack_start(self.sidebar, True, True, 0)
        self.leaflet.add(self.sidebar_box)
        self.leaflet.add(separator)
        self.leaflet.add(self.webview)
        self.leaflet.connect('notify::folded', self.on_main_leaflet_folded)

        self.size_group_left = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.size_group_right = Gtk.SizeGroup(Gtk.SizeGroupMode.HORIZONTAL)
        self.size_group_left.add_widget(self.sidebar_box)
        self.size_group_right.add_widget(self.webview)
        self.headerbar = GFeedHeaderbar(
            self.size_group_left,
            self.size_group_right,
            self.on_back_button_clicked,
            self.webview
        )
        
        self.headerbar.stack_switcher.set_stack(self.sidebar)
        self.headerbar.connect(
            'gfeeds_headerbar_squeeze',
            self.on_headerbar_squeeze
        )

        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.bottom_bar = Handy.ViewSwitcherBar()
        self.bottom_bar.set_stack(self.sidebar)
        self.main_box.pack_end(self.bottom_bar, False, False, 0)

        self.set_headerbar_or_titlebar()
        self.confman.connect(
            'gfeeds_enable_csd_changed',
            self.set_headerbar_or_titlebar
        )

        self.add(self.main_box)
        self.main_box.pack_end(self.leaflet, True, True, 0)

        # Why this -52?
        # because every time a new value is saved, for some reason
        # it's the actual value +52 out of nowhere
        # this makes the window ACTUALLY preserve its old size
        self.resize(
            self.confman.conf['windowsize']['width']-52,
            self.confman.conf['windowsize']['height']-52
        )
        self.size_allocation = self.get_allocation()
        self.connect('size-allocate', self.update_size_allocation)
        self.on_main_leaflet_folded()

        # accel_group is for keyboard shortcuts
        self.accel_group = Gtk.AccelGroup()
        self.add_accel_group(self.accel_group)
        shortcuts_l = [
            {
                'combo': '<Control>q',
                'cb': self.emit_destroy
            },
            {
                'combo': '<Control>r',
                'cb': self.feedman.refresh
            },
            {
                'combo': '<Control>j',
                'cb': self.sidebar.select_next_article
            },
            {
                'combo': '<Control>k',
                'cb': self.sidebar.select_prev_article
            },
            {
                'combo': '<Control>plus',
                'cb': self.webview.key_zoom_in
            },
            {
                'combo': '<Control>minus',
                'cb': self.webview.key_zoom_out
            },
            {
                'combo': '<Control>equal',
                'cb': self.webview.key_zoom_reset
            }
        ]
        for s in shortcuts_l:
            self.add_accelerator(s['combo'], s['cb'])

    def on_headerbar_squeeze(self, caller, squeezed):
        self.bottom_bar.set_reveal(squeezed)

    def set_headerbar_or_titlebar(self, *args):
        if self.confman.conf['enable_csd']:
            if self.headerbar in self.main_box.get_children():
                self.main_box.remove(self.headerbar)
                for h in [
                    self.headerbar.left_headerbar,
                    self.headerbar.right_headerbar,
                    self.headerbar]:
                    h.get_style_context().remove_class('notheaderbar')
            self.set_titlebar(self.headerbar)
        else:
            self.set_titlebar(None)
            self.main_box.pack_start(self.headerbar, False, False, 0)
            for h in [
                    self.headerbar.left_headerbar,
                    self.headerbar.right_headerbar,
                    self.headerbar]:
                h.get_style_context().add_class('notheaderbar')

    def add_accelerator(self, shortcut, callback):
        if shortcut:
            key, mod = Gtk.accelerator_parse(shortcut)
            self.accel_group.connect(key, mod, Gtk.AccelFlags.VISIBLE, callback)

    def emit_destroy(self, *args):
        self.emit('destroy')

    def on_destroy(self, *args):
        self.confman.conf['windowsize'] = {
            'width': self.size_allocation.width,
            'height': self.size_allocation.height
        }
        # cleanup old read items
        feeds_items_links = [fi.link for fi in self.feedman.feeds_items]
        to_rm = []
        for ri in self.confman.conf['read_items']:
            if not ri in feeds_items_links:
                to_rm.append(ri)
        for ri in to_rm:
            self.confman.conf['read_items'].pop(
                self.confman.conf['read_items'].index(ri)
            )
        self.confman.save_conf()

    def on_sidebar_row_activated(self, listbox, row):
        row.popover.set_read(True)
        other_listbox = (
            self.sidebar.listbox
            if listbox == self.sidebar.saved_items_listbox
            else self.sidebar.saved_items_listbox
        )
        for other_row in other_listbox:
            if other_row.feeditem.link == row.feeditem.link:
                other_row.popover.set_read(True)
                break
        if self.confman.conf['use_rss_content']:
            self.webview.on_load_start()
            self.webview.set_enable_rss_content(None, True, row.feeditem)
        else:
            self.webview.load_feeditem(row.feeditem)
        self.headerbar.open_externally_btn.set_sensitive(True)
        self.leaflet.set_visible_child(self.webview)
        self.headerbar.leaflet.set_visible_child(self.headerbar.right_headerbar)
        self.on_main_leaflet_folded()
        listbox.invalidate_filter()
        other_listbox.invalidate_filter()

    def on_main_leaflet_folded(self, *args):
        target = None
        # other = None
        if self.leaflet.folded:
            target = self.headerbar.leaflet.get_visible_child()
            self.headerbar.back_button.show()
        else:
            if self.confman.wm_decoration_on_left:
                target = self.headerbar.left_headerbar
            else:
                target = self.headerbar.right_headerbar
            self.headerbar.back_button.hide()
        self.headerbar.headergroup.set_focus(target)

    def on_back_button_clicked(self, *args):
        self.leaflet.set_visible_child(self.sidebar_box)
        self.on_main_leaflet_folded()

    def update_size_allocation(self, *args):
        self.size_allocation = self.get_allocation()
