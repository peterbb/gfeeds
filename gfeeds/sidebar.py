from gi.repository import Gtk
from xml.sax.saxutils import escape

class GFeedsSidebarRow(Gtk.ListBoxRow):
    def __init__(self, feeditem, **kwargs):
        super().__init__(**kwargs)
        self.feeditem = feeditem
        
        self.title_label = Gtk.Label(f'<big><b>{escape(self.feeditem.title)}</b></big>')
        self.origin_label = Gtk.Label(f'<i>{escape(self.feeditem.parent_feed.title)}</i>')
        self.date_label = Gtk.Label(str(self.feeditem.pub_date))
        self.labels = [self.title_label, self.origin_label, self.date_label]
        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        for l in self.labels:
            l.set_use_markup(True)
            l.set_line_wrap(True)
            l.set_hexpand(False)
            l.set_halign(Gtk.Align.START)
            self.box.pack_start(l, False, False, 3)

        self.add(self.box)

class GFeedsSidebarListBox(Gtk.ListBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

    def populate(self, feeditems_l):
        while True:
            row = self.get_row_at_index(0)
            if row:
                self.remove(row)
            else:
                break
        for i in feeditems_l:
            self.add(GFeedsSidebarRow(i))
            self.show_all()

class GFeedsSidebar(Gtk.ScrolledWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listbox = GFeedsSidebarListBox()
        self.populate = self.listbox.populate
        self.set_size_request(300, 500)
        
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(self.listbox)
