from gettext import gettext as _
from xml.sax.saxutils import escape
from gi.repository import Gtk, Pango
from gfeeds.feeds_manager import FeedsManager
from gfeeds.confManager import ConfManager
from gfeeds.scrolled_message_dialog import ScrolledMessageDialog


class GFeedsInfoBar(Gtk.InfoBar):
    def __init__(self, text, icon_name=None,
                 message_type=Gtk.MessageType.INFO, **kwargs):
        super().__init__(**kwargs)
        self.set_message_type(message_type)
        self.text = text
        self.container_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.label = Gtk.Label(label=self.text)
        self.label.set_line_wrap(True)
        self.label.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.label.set_xalign(0.0)
        if icon_name:
            self.icon_name = icon_name
            self.icon = Gtk.Image.new_from_icon_name(
                self.icon_name,
                Gtk.IconSize.BUTTON
            )
            self.container_box.pack_start(self.icon, False, False, 6)
        self.container_box.pack_start(self.label, False, False, 6)
        self.container_box.set_halign(Gtk.Align.CENTER)
        self.container_box.set_margin_top(6)
        self.container_box.set_margin_bottom(6)
        self.get_content_area().set_center_widget(self.container_box)
        self.set_hexpand(False)
        # self.set_size_request(360, -1)


class GFeedsErrorsBar(GFeedsInfoBar):
    def __init__(self, parent_win, **kwargs):
        super().__init__(
            text=_('There are some errors'),
            icon_name='computer-fail-symbolic',
            message_type=Gtk.MessageType.INFO,
            **kwargs
        )
        self.confman = ConfManager()
        self.parent_win = parent_win
        self.errors = []
        self.problematic_feeds = []
        self.show_button = Gtk.Button(label=_('Show'))
        self.ignore_button = Gtk.Button(label=_('Ignore'))
        self.show_button.connect('clicked', self.show_errors)
        self.ignore_button.connect(
            'clicked',
            lambda *args: self.set_revealed(False)
        )
        self.container_box.pack_end(self.ignore_button, False, False, 6)
        self.container_box.pack_end(self.show_button, False, False, 6)
        self.set_revealed(False)

    def engage(self, errors: list, problematic_feeds: list):
        self.errors = errors
        self.problematic_feeds = problematic_feeds
        if len(errors) != 0:
            self.set_revealed(True)

    def show_errors(self, *args):
        dialog = ScrolledMessageDialog(
            self.parent_win,
            Gtk.DialogFlags.MODAL | Gtk.DialogFlags.DESTROY_WITH_PARENT,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.YES_NO,
            _(
                'There were problems with some feeds. '
                'Do you want to remove them?'
            )
        )
        dialog.format_secondary_markup(
            escape('\n'.join(self.errors))
        )
        if (dialog.run() == Gtk.ResponseType.YES):
            for pf in self.problematic_feeds:
                if pf in self.confman.conf['feeds'].keys():
                    self.confman.conf['feeds'].pop(pf)
            self.set_revealed(False)
        else:
            self.set_revealed(True)
        dialog.close()


class GFeedsConnectionBar(GFeedsInfoBar):
    def __init__(self, **kwargs):
        super().__init__(
            text=_('You are offline'),
            icon_name='network-offline-symbolic',
            message_type=Gtk.MessageType.INFO,
            **kwargs
        )
        self.container_box.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.feedman = FeedsManager()
        self.feedman.connect(
            'feedmanager_online_changed',
            lambda caller, value: self.set_revealed(not value)
        )
        self.set_revealed(False)
