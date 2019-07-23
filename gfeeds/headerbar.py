from gettext import gettext as _
from gi.repository import Gtk, Handy
from .leaflet import GFeedsLeaflet

class GFeedHeaderbar(Handy.TitleBar):
    def __init__(self, size_group_left, size_group_right, open_externally_func, back_btn_func, **kwargs):
        super().__init__(**kwargs)
        self.back_btn_func = back_btn_func
        
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
        self.open_externally_btn.connect('clicked', open_externally_func)
        self.right_headerbar.pack_end(self.open_externally_btn)

        self.menu_btn = Gtk.Button.new_from_icon_name(
            'open-menu-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.menu_btn.set_tooltip_text('Menu')
        self.menu_popover = Gtk.PopoverMenu()
        self.menu_builder = Gtk.Builder.new_from_resource('/org/gabmus/gnome-feeds/ui/menu.xml')
        self.menu = self.menu_builder.get_object('generalMenu')
        self.menu_popover.bind_model(self.menu)
        self.menu_popover.set_relative_to(self.menu_btn)
        self.menu_popover.set_modal(True)
        self.menu_btn.connect('clicked', self.on_menu_btn_clicked)
        self.left_headerbar.pack_end(self.menu_btn)

    def on_back_button_clicked(self, *args):
        self.leaflet.set_visible_child(self.left_headerbar)
        self.back_btn_func()

    def on_menu_btn_clicked(self, *args):
        self.menu_popover.popup()
