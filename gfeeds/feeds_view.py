from gettext import gettext as _
from gi.repository import Gtk
from os.path import isfile
from .confManager import ConfManager
from .feeds_manager import FeedsManager

class FeedsViewAllListboxRow(Gtk.ListBoxRow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.IS_ALL = True
        self.feed = None
        self.label = Gtk.Label()
        self.label.set_markup(
            '<big><b>' +
            _('All feeds') +
            '</b></big>'
        )
        self.label.set_use_markup(True)
        self.label.set_margin_top(12)
        self.label.set_margin_bottom(12)
        self.add(self.label)

class FeedsViewListboxRow(Gtk.ListBoxRow):
    def __init__(self, feed, **kwargs):
        super().__init__(**kwargs)
        self.IS_ALL = False
        self.feed = feed
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/manage_feeds_listbox_row.glade'
        )
        self.hbox = self.builder.get_object('hbox')
        self.checkbox = self.builder.get_object('check')
        self.checkbox.set_no_show_all(True)
        self.checkbox.hide()
        self.icon = self.builder.get_object('icon')
        if isfile(self.feed.favicon_path):
            self.icon.set_from_file(self.feed.favicon_path)
        self.name_label = self.builder.get_object('title_label')
        self.name_label.set_text(self.feed.title)
        self.desc_label = self.builder.get_object('description_label')
        self.desc_label.set_text(self.feed.description)
        self.add(self.hbox)


class FeedsViewListbox(Gtk.ListBox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feedman = FeedsManager()
        self.confman = ConfManager()

        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.connect('row-activated', self.on_row_activated)

        for feed in self.feedman.feeds:
            self.add_feed(feed)
        self.feedman.feeds.connect(
            'empty',
            lambda *args: self.empty()
        )
        self.feedman.feeds.connect(
            'append',
            lambda caller, feed: self.add_feed(feed)
        )
        self.feedman.feeds.connect(
            'pop',
            lambda caller, feed: self.remove_feed(feed)
        )

        self.set_sort_func(self.gfeeds_sort_func, None, False)

    def add_feed(self, feed):
        self.add(FeedsViewListboxRow(feed))

    def add(self, *args, **kwargs):
        super().add(*args, **kwargs)
        self.show_all()

    def on_row_activated(self, listbox, row):
        if row.IS_ALL:
            self.confman.emit('gfeeds_filter_changed', None)
            return
        self.confman.emit('gfeeds_filter_changed', row.feed)

    def remove_feed(self, feed):
        for row in self.get_children():
            if not row.IS_ALL:
                if row.feed == feed:
                    self.remove(row)
                    break

    def empty(self):
        while True:
            row = self.get_row_at_index(1)
            if row:
                if not row.IS_ALL:
                    self.remove(row)
            else:
                break

    def gfeeds_sort_func(self, row1, row2, data, notify_destroy):
        if row1.IS_ALL:
            return False
        elif row2.IS_ALL:
            return True
        else:
            return row1.feed.title.lower() > row2.feed.title.lower()


class FeedsViewScrolledWindow(Gtk.ScrolledWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listbox = FeedsViewListbox()
        self.all_row = FeedsViewAllListboxRow()
        self.listbox.add(self.all_row)
        self.listbox.select_row(self.all_row)
        # self.set_size_request(300, 500)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.add(self.listbox)
        self.set_size_request(250, 400)
        self.get_style_context().add_class('frame')
        self.set_margin_top(6)
        self.set_margin_right(6)
        self.set_margin_bottom(6)
        self.set_margin_left(6)

class FeedsViewPopover(Gtk.Popover):
    def __init__(self, relative_to, **kwargs):
        super().__init__(**kwargs)
        self.scrolled_win = FeedsViewScrolledWindow()
        self.add(self.scrolled_win)
        self.set_modal(True)
        self.set_relative_to(relative_to)
        relative_to.connect('clicked', self.on_relative_to_clicked)

    def on_relative_to_clicked(self, *args):
        self.popup()
        self.show_all()
