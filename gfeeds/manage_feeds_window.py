from gettext import gettext as _
from gi.repository import Gtk, Gdk
from xml.sax.saxutils import escape


class ManageFeedsHeaderbar(Gtk.HeaderBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title('Manage Feeds')
        self.set_show_close_button(True)


class ManageFeedsListboxRow(Gtk.ListBoxRow):
    def __init__(self, feed, **kwargs):
        super().__init__(**kwargs)

        self.feed = feed
        self.hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.checkbox = Gtk.CheckButton()
        self.icon = Gtk.Image.new_from_file(self.feed.favicon_path)
        self.name_label = Gtk.Label(f'<big><b>{escape(self.feed.title)}</b></big>')
        self.desc_label = Gtk.Label(f'<i>{escape(self.feed.description)}</i>')
        for l in [self.name_label, self.desc_label]:
            l.set_use_markup(True)
            l.set_line_wrap(True)
            l.set_hexpand(False)
            l.set_halign(Gtk.Align.START)
            self.vbox.pack_start(l, False, False, 3)
        self.hbox.pack_start(self.icon, False, False, 6)
        self.hbox.pack_start(self.vbox, True, True, 6)
        self.hbox.pack_start(self.checkbox, False, False, 6)
        self.add(self.hbox)



class ManageFeedsListbox(Gtk.ListBox):
    def __init__(self, feeds, **kwargs):
        super().__init__(**kwargs)

        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.connect('row-activated', self.on_row_activated)

        for feed in feeds:
            self.add(ManageFeedsListboxRow(feed))

        self.set_sort_func(self.gfeeds_sort_func, None, False)

    def on_row_activated(self, listbox, row):
        row.checkbox.set_active(not row.checkbox.get_active())

    def gfeeds_sort_func(self, row1, row2, data, notify_destroy):
        return row1.feed.title.lower() > row2.feed.title.lower()


class ManageFeedsScrolledWindow(Gtk.ScrolledWindow):
    def __init__(self, feeds, **kwargs):
        super().__init__(**kwargs)
        self.listbox = ManageFeedsListbox(feeds)
        self.set_size_request(300, 500)
        self.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        self.add(self.listbox)


class GFeedsManageFeedsWindow(Gtk.Window):
    def __init__(self, appwindow, feeds, **kwargs):
        super().__init__(**kwargs)


        self.scrolled_window = ManageFeedsScrolledWindow(feeds)
        self.listbox = self.scrolled_window.listbox
        self.headerbar = ManageFeedsHeaderbar()

        self.set_titlebar(self.headerbar)
        self.add(self.scrolled_window)

        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_transient_for(appwindow)
        self.set_attached_to(appwindow)

    def present(self, *args, **kwargs):
        super().present(*args, **kwargs)
        self.show_all()
