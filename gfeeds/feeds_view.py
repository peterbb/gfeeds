from gettext import gettext as _
from gi.repository import Gtk, Pango
from os.path import isfile
from gfeeds.confManager import ConfManager
from gfeeds.feeds_manager import FeedsManager
from gfeeds.initials_icon import InitialsIcon

class FeedsViewAllListboxRow(Gtk.ListBoxRow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.IS_ALL = True
        self.feed = None
        self.label = Gtk.Label()
        self.label.set_markup(
            '<b>' +
            _('All feeds') +
            '</b>'
        )
        self.label.set_use_markup(True)
        self.label.set_margin_top(12)
        self.label.set_margin_bottom(12)
        self.add(self.label)

class FeedsViewListboxRow(Gtk.ListBoxRow):
    def __init__(self, feed, description=True, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.IS_ALL = False
        self.feed = feed
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/manage_feeds_listbox_row.glade'
        )
        self.hbox = self.builder.get_object('hbox')
        self.checkbox = self.builder.get_object('check')
        self.checkbox.set_no_show_all(True)
        self.checkbox.hide()

        self.icon_container = self.builder.get_object('icon_container')
        if isfile(self.feed.favicon_path):
            self.icon = Gtk.Image.new_from_file(
                self.feed.favicon_path
            )
        else:
            self.icon = InitialsIcon(self.feed.title)
        self.icon_container.add(self.icon)

        self.name_label = self.builder.get_object('title_label')
        self.name_label.set_text(self.feed.title)
        self.confman.connect(
            'gfeeds_full_feed_name_changed',
            self.on_full_feed_name_changed
        )
        self.desc_label = self.builder.get_object('description_label')
        self.desc_label.set_no_show_all(not description)
        if description:
            self.desc_label.set_text(self.feed.description)
        else:
            self.desc_label.hide()
            self.name_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.add(self.hbox)
        self.on_full_feed_name_changed()

    def on_full_feed_name_changed(self, *args):
        self.name_label.set_ellipsize(
            Pango.EllipsizeMode.NONE if self.confman.conf['full_feed_name']
            else Pango.EllipsizeMode.END
        )


class FeedsViewListbox(Gtk.ListBox):
    def __init__(self, description=True, **kwargs):
        super().__init__(**kwargs)
        self.description = description
        self.feedman = FeedsManager()
        self.confman = ConfManager()

        self.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.connect('row-activated', self.on_row_activated)

        for feed in self.feedman.feeds:
            self.add_feed(feed)
        self.feedman.feeds.connect(
            'empty',
            self.empty
        )
        self.feedman.feeds.connect(
            'append',
            self.on_feeds_append
        )
        self.feedman.feeds.connect(
            'pop',
            self.on_feeds_pop
        )

        self.set_sort_func(self.gfeeds_sort_func, None, False)
        self.set_header_func(self.separator_header_func)

    def separator_header_func(self, row, prev_row=None):
        if (
            prev_row != None and
            row.get_header() == None
        ):
            separator = Gtk.Separator(orientation = Gtk.Orientation.HORIZONTAL)
            row.set_header(separator)

    def on_feeds_pop(self, caller, feed):
        self.remove_feed(feed)

    def on_feeds_append(self, caller, feed):
        self.add_feed(feed)

    def add_feed(self, feed):
        self.add(FeedsViewListboxRow(feed, self.description))

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

    def empty(self, *args):
        while True:
            row = self.get_row_at_index(1)
            if row:
                if not row.IS_ALL:
                    self.remove(row)
            else:
                break

    def row_all_activate(self):
        for row in self.get_children():
            if row.IS_ALL:
                row.activate()

    def gfeeds_sort_func(self, row1, row2, data, notify_destroy):
        if row1.IS_ALL:
            return False
        elif row2.IS_ALL:
            return True
        else:
            return row1.feed.title.lower() > row2.feed.title.lower()


class FeedsViewScrolledWindow(Gtk.ScrolledWindow):
    def __init__(self, description=True, **kwargs):
        super().__init__(**kwargs)
        self.listbox = FeedsViewListbox(description)
        self.all_row = FeedsViewAllListboxRow()
        self.listbox.add(self.all_row)
        self.listbox.select_row(self.all_row)
        # self.set_size_request(360, 500)
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
        self.scrolled_win = FeedsViewScrolledWindow(description=False)
        self.add(self.scrolled_win)
        self.set_modal(True)
        self.set_relative_to(relative_to)
        relative_to.connect('clicked', self.on_relative_to_clicked)

    def on_relative_to_clicked(self, *args):
        self.popup()
        self.show_all()
