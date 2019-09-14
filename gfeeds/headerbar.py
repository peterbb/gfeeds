from gettext import gettext as _
from gi.repository import Gtk, Gdk, Handy, GObject
from .confManager import ConfManager
from .feeds_manager import FeedsManager
from .spinner_button import RefreshSpinnerButton
from .feeds_view import FeedsViewPopover

class AddFeedPopover(Gtk.Popover):
    def __init__(self, relative_to, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.feedman = FeedsManager()
        
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/add_feed_box.glade'
        )
        self.set_modal(True)
        self.set_relative_to(relative_to)
        relative_to.connect('clicked', self.on_relative_to_clicked)
        self.container_box = self.builder.get_object('container_box')
        self.confirm_btn = self.builder.get_object('confirm_btn')
        self.confirm_btn.connect(
            'clicked',
            self.on_confirm_btn_clicked
        )
        self.url_entry = self.builder.get_object('url_entry')
        self.already_subscribed_revealer = self.builder.get_object(
            'already_subscribed_revealer'
        )
        self.url_entry.connect(
            'changed',
            lambda *args: self.already_subscribed_revealer.set_reveal_child(False)
        )
        self.add(self.container_box)

    def on_relative_to_clicked(self, *args):
        self.popup()

    def on_confirm_btn_clicked(self, btn):
        res = self.feedman.add_feed(self.url_entry.get_text(), True)
        if res:
            self.popdown()
            self.already_subscribed_revealer.set_reveal_child(False)
        else:
            self.already_subscribed_revealer.set_reveal_child(True)


class GFeedHeaderbar(Handy.TitleBar):
    __gsignals__ = {
        'gfeeds_headerbar_squeeze': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (bool,)
        )
    }
    def __init__(
            self,
            size_group_left,
            size_group_right,
            back_btn_func,
            webview,
            **kwargs):
        super().__init__(**kwargs)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/headerbar.glade'
        )
        self.builder.connect_signals(self)
        self.confman = ConfManager()
        self.feedman = FeedsManager()
        self.back_btn_func = back_btn_func
        self.webview = webview
        self.webview.connect('gfeeds_webview_load_start', self.on_load_start)
        self.webview.connect('gfeeds_webview_load_end', self.on_load_end)
        self.headergroup = Handy.HeaderGroup()
        self.leaflet = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/gfeeds_leaflet.glade'
        ).get_object('leaflet')
        self.left_headerbar = self.builder.get_object(
            'left_headerbar'
        )
        self.right_headerbar = self.builder.get_object(
            'right_headerbar'
        )
        self.right_headerbar.set_hexpand(True)
        size_group_left.add_widget(self.left_headerbar)
        size_group_right.add_widget(self.right_headerbar)
        self.headergroup.add_header_bar(self.left_headerbar)
        self.headergroup.add_header_bar(self.right_headerbar)
        separator = Gtk.Separator()
        separator.get_style_context().add_class('sidebar')

        self.leaflet.add(self.left_headerbar)
        self.leaflet.add(separator)
        self.leaflet.add(self.right_headerbar)
        self.add(self.leaflet)
        self.set_headerbar_controls()
        self.confman.connect(
            'gfeeds_enable_csd_changed',
            self.set_headerbar_controls
        )
        self.headergroup.set_focus(self.left_headerbar)

        self.back_button = self.builder.get_object(
            'back_btn'
        )
        self.open_externally_btn = self.builder.get_object(
            'open_externally_btn'
        )
        self.open_externally_btn.connect(
            'clicked',
            self.webview.open_externally
        )
        self.reader_mode_btn = self.builder.get_object(
            'reader_btn'
        )
        self.reader_mode_btn_handler_id = self.reader_mode_btn.connect(
            'toggled',
            self.on_reader_mode_toggled
        )
        self.rss_content_btn = self.builder.get_object(
            'rss_content_btn'
        )
        self.rss_content_btn_handler_id = self.rss_content_btn.connect(
            'toggled',
            self.on_rss_content_toggled
        )
        self.share_btn = self.builder.get_object(
            'share_btn'
        )
        self.menu_btn = self.builder.get_object(
            'menu_btn'
        )
        self.menu_popover = Gtk.PopoverMenu()
        self.menu_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/menu.xml'
        )
        self.menu = self.menu_builder.get_object('generalMenu')
        self.menu_popover.bind_model(self.menu)
        self.menu_popover.set_relative_to(self.menu_btn)
        self.menu_popover.set_modal(True)

        self.search_btn = self.builder.get_object('search_btn')
        self.filter_btn = self.builder.get_object(
            'filter_btn'
        )
        self.filter_popover = FeedsViewPopover(self.filter_btn)
        self.feedman.connect(
            'feedmanager_refresh_start',
            lambda *args: self.filter_popover.scrolled_win.listbox.row_all_activate()
        )

        self.add_btn = self.builder.get_object(
            'add_btn'
        )
        self.add_btn.set_tooltip_text(_('Add new feed'))
        self.add_popover = AddFeedPopover(self.add_btn)

        self.refresh_btn = RefreshSpinnerButton()
        self.refresh_btn.btn.connect('clicked', self.feedman.refresh)
        self.builder.get_object('refresh_btn_box').add(self.refresh_btn)

        self.squeezer = Handy.Squeezer(orientation=Gtk.Orientation.HORIZONTAL)
        self.squeezer.set_homogeneous(False)
        self.squeezer.set_interpolate_size(False)
        self.squeezer.set_hexpand(False)
        self.nobox = Gtk.Label()
        self.nobox.set_size_request(1, -1)
        self.stack_switcher = Handy.ViewSwitcher()
        self.stack_switcher.set_policy(Handy.ViewSwitcherPolicy.WIDE)
        self.stack_switcher.set_margin_left(12)
        self.stack_switcher.set_margin_right(12)
        self.squeezer.add(self.stack_switcher)
        self.squeezer.add(self.nobox)
        self.squeezer.connect('notify::visible-child', self.on_squeeze)
        self.left_headerbar.set_custom_title(self.squeezer)

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        self.feedman.connect(
            'feedmanager_refresh_start',
            self.on_new_feed_add_start
        )
        self.feedman.connect(
            'feedmanager_refresh_end',
            self.on_new_feed_add_end
        )
        self.title_label = self.builder.get_object('title_label')
        self.title_label.set_hexpand(False)

    def set_article_title(self, title):
        self.title_label.set_text(title)

    def on_squeeze(self, *args):
        self.emit(
            'gfeeds_headerbar_squeeze',
            self.squeezer.get_visible_child() == self.nobox
        )

    def on_search_btn_toggled(self, togglebtn):
        searchbar = self.get_parent().searchbar
        searchbar.set_search_mode(togglebtn.get_active())

    def on_reader_mode_toggled(self, togglebtn):
        with self.rss_content_btn.handler_block(self.rss_content_btn_handler_id):
            self.rss_content_btn.set_active(False)
            self.webview.set_enable_reader_mode(togglebtn)

    def on_rss_content_toggled(self, togglebtn):
        with self.reader_mode_btn.handler_block(self.reader_mode_btn_handler_id):
            self.reader_mode_btn.set_active(False)
            self.webview.set_enable_rss_content(togglebtn)

    def on_new_feed_add_start(self, *args):
        self.refresh_btn.set_spinning(True)
        self.add_popover.confirm_btn.set_sensitive(False)

    def on_new_feed_add_end(self, *args):
        self.refresh_btn.set_spinning(False)
        self.add_popover.confirm_btn.set_sensitive(True)
        self.add_popover.url_entry.set_text('')

    def set_headerbar_controls(self, *args):
        if self.confman.conf['enable_csd']:
            self.right_headerbar.set_show_close_button(True)
            self.left_headerbar.set_show_close_button(True)
        else:
            self.right_headerbar.set_show_close_button(False)
            self.left_headerbar.set_show_close_button(False)

    def on_back_button_clicked(self, *args):
        self.leaflet.set_visible_child(self.left_headerbar)
        self.back_btn_func()

    def on_menu_btn_clicked(self, *args):
        self.menu_popover.popup()

    def on_load_start(self, *args):
        self.reader_mode_btn.set_sensitive(False)
        self.rss_content_btn.set_sensitive(False)
        with self.reader_mode_btn.handler_block(self.reader_mode_btn_handler_id):
            self.reader_mode_btn.set_active(
                self.confman.conf['default_reader'] and
                not self.confman.conf['use_rss_content']
            )
        with self.rss_content_btn.handler_block(self.rss_content_btn_handler_id):
            self.rss_content_btn.set_active(
                self.confman.conf['use_rss_content']
            )

    def on_load_end(self, *args):
        self.reader_mode_btn.set_sensitive(True)
        self.rss_content_btn.set_sensitive(True)

    def copy_article_uri(self, *args):
        self.clipboard.set_text(self.webview.uri, -1)
        self.clipboard.store()
        self.webview.show_notif()
