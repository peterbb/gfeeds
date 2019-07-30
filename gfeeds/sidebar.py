from gi.repository import Gtk
from xml.sax.saxutils import escape
from .confManager import ConfManager

class GFeedsSidebarRow(Gtk.ListBoxRow):
    def __init__(self, feeditem, **kwargs):
        super().__init__(**kwargs)
        self.feeditem = feeditem
        self.super_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)

        self.title_label = Gtk.Label(f'<big><b>{escape(self.feeditem.title)}</b></big>')
        self.origin_label = Gtk.Label(f'<i>{escape(self.feeditem.parent_feed.title)}</i>')
        self.date_label = Gtk.Label(str(self.feeditem.pub_date))
        self.icon = Gtk.Image.new_from_file(self.feeditem.parent_feed.favicon_path)
        self.super_box.pack_start(self.icon, False, False, 6)
        self.labels = [self.title_label, self.origin_label, self.date_label]
        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        for l in self.labels:
            l.set_use_markup(True)
            l.set_line_wrap(True)
            l.set_hexpand(False)
            l.set_halign(Gtk.Align.START)
            self.box.pack_start(l, False, False, 3)

        self.super_box.pack_start(self.box, True, True, 6)
        self.add(self.super_box)

class GFeedsSidebarListBox(Gtk.ListBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.get_style_context().add_class('sidebar')

        self.set_sort_from_confman()
        self.confman.connect(
            'gfeeds_new_first_changed',
            self.set_sort_from_confman
        )
        self.get_style_context().add_class('sidebar')

    def set_sort_from_confman(self, *args):
        if self.confman.conf['new_first']:
            self.set_sort_func(self.gfeeds_sort_new_first_func, None, False)
        else:
            self.set_sort_func(self.gfeeds_sort_old_first_func, None, False)

    def add_new_items(self, feeditems_l):
        for i in feeditems_l:
            self.add(GFeedsSidebarRow(i))
            self.show_all()

    def empty(self):
        while True:
            row = self.get_row_at_index(0)
            if row:
                self.remove(row)
            else:
                break

    def populate(self, feeditems_l):
        self.empty()
        self.add_new_items(feeditems_l)

    def gfeeds_sort_new_first_func(self, row1, row2, data, notify_destroy):
        return row1.feeditem.pub_date < row2.feeditem.pub_date

    def gfeeds_sort_old_first_func(self, row1, row2, data, notify_destroy):
        return row1.feeditem.pub_date > row2.feeditem.pub_date


class GFeedsSidebar(Gtk.ScrolledWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listbox = GFeedsSidebarListBox()
        self.empty = self.listbox.empty
        self.populate = self.listbox.populate
        self.set_size_request(300, 500)
        
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(self.listbox)

    def select_next_article(self, *args):
        target = None
        current_row = self.listbox.get_selected_row()
        if not current_row:
            target = self.listbox.get_row_at_index(0)
        else:
            target = self.listbox.get_row_at_index(
                current_row.get_index()+1
            )
        if target:
            self.listbox.select_row(target)
            self.listbox.emit('row-activated', target)

    def select_prev_article(self, *args):
        target = None
        current_row = self.listbox.get_selected_row()
        if not current_row:
            return
        else:
            target = self.listbox.get_row_at_index(
                current_row.get_index()-1
            )
        if target:
            self.listbox.select_row(target)
            self.listbox.emit('row-activated', target)
