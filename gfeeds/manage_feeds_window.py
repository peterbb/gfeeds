from gettext import gettext as _
from gi.repository import Gtk, Gdk
from xml.sax.saxutils import escape


class ManageFeedsHeaderbar(Gtk.HeaderBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.set_title(_('Manage Feeds'))
        self.set_show_close_button(True)

        self.select_all_btn = Gtk.Button.new_from_icon_name(
            'edit-select-all-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.select_all_btn.set_tooltip_text(_('Select/Unselect all'))

        self.delete_btn = Gtk.Button.new_from_icon_name(
            'user-trash-symbolic',
            Gtk.IconSize.BUTTON
        )
        self.delete_btn.set_tooltip_text(_('Delete selected feeds'))
        self.delete_btn.get_style_context().add_class('destructive-action')
        self.delete_btn.set_sensitive(False)

        self.pack_end(self.delete_btn)
        self.pack_start(self.select_all_btn)

class ManageFeedsListboxRow(Gtk.ListBoxRow):
    def __init__(self, feed, **kwargs):
        super().__init__(**kwargs)

        self.feed = feed
        self.hbox = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.vbox = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.checkbox = Gtk.CheckButton()
        self.checkbox_handler_id = self.checkbox.connect(
            'toggled',
            self.on_checkbox_toggled
        )
        self.icon = Gtk.Image.new_from_file(self.feed.favicon_path)
        self.name_label = Gtk.Label(f'<big><b>{escape(self.feed.title)}</b></big>')
        self.desc_label = Gtk.Label(f'<i>{escape(self.feed.description)}</i>')
        for l in [self.name_label, self.desc_label]:
            l.set_use_markup(True)
            l.set_line_wrap(True)
            l.set_hexpand(False)
            l.set_halign(Gtk.Align.START)
            l.set_xalign(0)
            self.vbox.pack_start(l, False, False, 3)
        self.hbox.pack_start(self.icon, False, False, 6)
        self.hbox.pack_start(self.vbox, True, True, 6)
        self.hbox.pack_start(self.checkbox, False, False, 6)
        self.add(self.hbox)

    def on_checkbox_toggled(self, checkbox):
        with checkbox.handler_block(self.checkbox_handler_id):
            checkbox.set_active(not checkbox.get_active())
        self.emit('activate')


class ManageFeedsListbox(Gtk.ListBox):
    def __init__(self, feeds, **kwargs):
        super().__init__(**kwargs)

        self.set_selection_mode(Gtk.SelectionMode.NONE)
        self.connect('row-activated', self.on_row_activated)

        for feed in feeds:
            self.add(ManageFeedsListboxRow(feed))

        self.set_sort_func(self.gfeeds_sort_func, None, False)

    def on_row_activated(self, listbox, row):
        with row.checkbox.handler_block(row.checkbox_handler_id):
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

class DeleteFeedsConfirmMessageDialog(Gtk.MessageDialog):
    def __init__(self, parent, selected_feeds, **kwargs):
        super().__init__(
            parent,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            _('Do you want to delete these feeds?'),
            **kwargs
        )

        self.format_secondary_markup(
            '\n'.join([escape(f.title) for f in selected_feeds])
        )

class GFeedsManageFeedsWindow(Gtk.Window):
    def __init__(self, appwindow, feeds, **kwargs):
        super().__init__(**kwargs)
        self.appwindow = appwindow

        self.scrolled_window = ManageFeedsScrolledWindow(feeds)
        self.listbox = self.scrolled_window.listbox
        self.headerbar = ManageFeedsHeaderbar()

        self.headerbar.delete_btn.connect(
            'clicked',
            self.on_delete_clicked
        )
        self.headerbar.select_all_btn.connect(
            'clicked',
            self.on_select_all_clicked
        )
        self.listbox.connect('row-activated', self.on_row_activated)

        self.set_titlebar(self.headerbar)
        self.add(self.scrolled_window)

        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_transient_for(self.appwindow)
        self.set_attached_to(self.appwindow)

    def present(self, *args, **kwargs):
        super().present(*args, **kwargs)
        self.show_all()

    def on_delete_clicked(self, *args):
        selected_feeds = []
        for row in self.listbox.get_children():
            if row.checkbox.get_active():
                selected_feeds.append(row.feed)
        dialog = DeleteFeedsConfirmMessageDialog(self, selected_feeds)
        res = dialog.run()
        dialog.close()
        if res == Gtk.ResponseType.YES:
            selected_feeds_links = [f.rss_link for f in selected_feeds]
            for f in selected_feeds_links:
                self.appwindow.confman.conf['feeds'].pop(
                    self.appwindow.confman.conf['feeds'].index(f)
                )
            self.appwindow.confman.save_conf()
            self.appwindow.refresh_feeds()
            if len(self.appwindow.confman.conf['feeds']) == 0:
                self.appwindow.sidebar.set_main_visible(False)
            self.close()
        else:
            pass

    def on_select_all_clicked(self, *args):
        unselect = True
        for row in self.listbox.get_children():
            if not row.checkbox.get_active():
                unselect = False
                row.emit('activate')
        if unselect:
            for row in self.listbox.get_children():
                row.emit('activate')

    def on_row_activated(self, listbox, activated_row):
        for row in listbox.get_children():
            if row.checkbox.get_active():
                self.headerbar.delete_btn.set_sensitive(True)
                return
        self.headerbar.delete_btn.set_sensitive(False)
