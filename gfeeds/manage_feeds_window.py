from gettext import gettext as _
from gi.repository import Gtk, Gdk
from xml.sax.saxutils import escape
from os.path import isfile
from .confManager import ConfManager
from .feeds_manager import FeedsManager
from .feeds_view import (
    FeedsViewListbox,
    FeedsViewListboxRow
)

class ManageFeedsHeaderbar(Gtk.HeaderBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()

        self.set_title(_('Manage Feeds'))
        self.set_show_close_button(self.confman.conf['enable_csd'])

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

class ManageFeedsListboxRow(FeedsViewListboxRow):
    def __init__(self, feed, **kwargs):
        super().__init__(feed, **kwargs)
        self.checkbox.set_no_show_all(False)
        self.checkbox_handler_id = self.checkbox.connect(
            'toggled',
            self.on_checkbox_toggled
        )

    def on_checkbox_toggled(self, checkbox):
        with checkbox.handler_block(self.checkbox_handler_id):
            checkbox.set_active(not checkbox.get_active())
        self.emit('activate')


class ManageFeedsListbox(FeedsViewListbox):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_selection_mode(Gtk.SelectionMode.NONE)

    def add_feed(self, feed):
        self.add(ManageFeedsListboxRow(feed))

    def on_row_activated(self, listbox, row):
        with row.checkbox.handler_block(row.checkbox_handler_id):
            row.checkbox.set_active(not row.checkbox.get_active())

class ManageFeedsScrolledWindow(Gtk.ScrolledWindow):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.listbox = ManageFeedsListbox()
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
    def __init__(self, appwindow, **kwargs):
        super().__init__(**kwargs)
        self.appwindow = appwindow
        self.confman = ConfManager()
        self.feedman = FeedsManager()
        self.main_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.scrolled_window = ManageFeedsScrolledWindow()
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
        self.set_title(_('Manage Feeds'))

        if self.confman.conf['enable_csd']:
            self.set_titlebar(self.headerbar)
        else:
            self.headerbar.set_title('')
            self.headerbar.get_style_context().add_class('notheaderbar')
            self.main_box.pack_start(self.headerbar, False, False, 0)

        self.main_box.pack_start(self.scrolled_window, True, True, 0)
        self.add(self.main_box)

        self.set_type_hint(Gdk.WindowTypeHint.DIALOG)
        self.set_modal(True)
        self.set_transient_for(self.appwindow)

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
            self.feedman.delete_feeds(selected_feeds)

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
