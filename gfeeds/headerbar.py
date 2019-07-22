from gi.repository import Gtk, Handy
from .leaflet import GFeedsLeaflet

class GFeedHeaderbar(Handy.TitleBar):
    def __init__(self, size_group_left, size_group_right, **kwargs):
        super().__init__(**kwargs)
        
        self.headergroup = Handy.HeaderGroup()
        self.leaflet = GFeedsLeaflet()
        self.left_headerbar = Gtk.HeaderBar()
        self.right_headerbar = Gtk.HeaderBar()
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
