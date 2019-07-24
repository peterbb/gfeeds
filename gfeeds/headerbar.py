from gettext import gettext as _
from gi.repository import Gtk, Handy
from .leaflet import GFeedsLeaflet
from .confManager import ConfManager

class AddFeedPopover(Gtk.Popover):
    def __init__(self, relative_to, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/add_feed_box.glade'
        )
        self.set_modal(True)
        self.set_relative_to(relative_to)
        relative_to.connect('clicked', self.on_relative_to_clicked)
        self.container_box = self.builder.get_object('container_box')
        self.confirm_btn = self.builder.get_object('confirm_btn')
        self.confirm_btn.connect('clicked', self.on_confirm_btn_clicked)
        self.url_entry = self.builder.get_object('url_entry')

        self.add(self.container_box)

    def on_confirm_btn_clicked(self, *args):
        # TODO:
        # 1. verify the new feed is an url and is not dead
        # 2. try to parse it and see if it's parsable
        # 3. add it to the config, SAVE THE CONFIG
        # 4. refresh the articles list, remember to keep datetime ordering
        print(self.url_entry.get_text())

    def on_relative_to_clicked(self, *args):
        self.popup()


class GFeedHeaderbar(Handy.TitleBar):
    def __init__(
            self,
            size_group_left,
            size_group_right,
            back_btn_func,
            webview,
            **kwargs):
        super().__init__(**kwargs)
        self.back_btn_func = back_btn_func
        self.webview = webview
        self.webview.connect('gfeeds_webview_load_start', self.on_load_start)
        self.webview.connect('gfeeds_webview_load_end', self.on_load_end)
        
        self.headergroup = Handy.HeaderGroup()
        self.leaflet = GFeedsLeaflet()
        self.left_headerbar = Gtk.HeaderBar()
        self.right_headerbar = Gtk.HeaderBar()
        self.right_headerbar.set_hexpand(True)
        size_group_left.add_widget(self.left_headerbar)
        size_group_right.add_widget(self.right_headerbar)
        self.headergroup.add_header_bar(self.left_headerbar)
        self.headergroup.add_header_bar(self.right_headerbar)

        self.leaflet.add(self.left_headerbar)
        self.leaflet.add(self.right_headerbar)
        self.add(self.leaflet)
        self.right_headerbar.set_show_close_button(True)
        self.left_headerbar.set_show_close_button(True)
        self.headergroup.set_focus(self.left_headerbar)

        self.back_button = Gtk.Button.new_from_icon_name(
            'go-previous-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.back_button.set_tooltip_text(_('Back to articles'))
        self.back_button.set_visible(False)
        self.back_button.set_no_show_all(True)
        self.back_button.connect('clicked', self.on_back_button_clicked)
        self.right_headerbar.pack_start(self.back_button)
        
        self.open_externally_btn = Gtk.Button.new_from_icon_name(
            'web-browser-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.open_externally_btn.set_tooltip_text(_('Open externally'))
        self.open_externally_btn.set_sensitive(False)
        self.open_externally_btn.connect('clicked', self.webview.open_externally)
        self.right_headerbar.pack_end(self.open_externally_btn)

        self.reader_mode_btn = Gtk.ToggleButton()
        self.reader_mode_btn.set_tooltip_text(_('Reader mode'))
        self.reader_mode_btn.add(Gtk.Image.new_from_icon_name(
            'ephy-reader-mode-symbolic',
            Gtk.IconSize.BUTTON
        ))
        self.reader_mode_btn.connect('toggled', self.webview.set_enable_reader_mode)
        self.reader_mode_btn.set_sensitive(False)
        self.right_headerbar.pack_start(self.reader_mode_btn)

        self.menu_btn = Gtk.Button.new_from_icon_name(
            'open-menu-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.menu_btn.set_tooltip_text(_('Menu'))
        self.menu_popover = Gtk.PopoverMenu()
        self.menu_builder = Gtk.Builder.new_from_resource('/org/gabmus/gnome-feeds/ui/menu.xml')
        self.menu = self.menu_builder.get_object('generalMenu')
        self.menu_popover.bind_model(self.menu)
        self.menu_popover.set_relative_to(self.menu_btn)
        self.menu_popover.set_modal(True)
        self.menu_btn.connect('clicked', self.on_menu_btn_clicked)
        self.left_headerbar.pack_end(self.menu_btn)

        self.add_btn = Gtk.Button.new_from_icon_name(
            'list-add-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.add_btn.set_tooltip_text(_('Add new feed'))
        self.add_popover = AddFeedPopover(self.add_btn)
        self.left_headerbar.pack_start(self.add_btn)

    def on_back_button_clicked(self, *args):
        self.leaflet.set_visible_child(self.left_headerbar)
        self.back_btn_func()

    def on_menu_btn_clicked(self, *args):
        self.menu_popover.popup()

    def on_load_start(self, *args):
        self.reader_mode_btn.set_sensitive(False)
        self.reader_mode_btn.set_active(False)

    def on_load_end(self, *args):
        self.reader_mode_btn.set_sensitive(True)
