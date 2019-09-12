from gi.repository import Gtk, Handy


class GFeedsSearchbar(Handy.SearchBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_hexpand(False)
        self.entry = Gtk.Entry()
        self.add(self.entry)
        self.set_show_close_button(True)
        self.set_search_mode(True)
        self.connect_entry(self.entry)
        self.show_all()
