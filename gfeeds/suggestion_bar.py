from gi.repository import Gtk
from .feeds_manager import FeedsManager
from gettext import gettext as _

class GFeedsInfoBar(Gtk.InfoBar):
    def __init__(self, text, icon_name = None, message_type=Gtk.MessageType.INFO, **kwargs):
        super().__init__(**kwargs)
        self.set_message_type(message_type)
        self.text = text
        self.container_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.label = Gtk.Label(self.text)
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
        self.get_content_area().set_center_widget(self.container_box) #, True, True, 0)
        self.set_hexpand(False)


class GFeedsConnectionBar(GFeedsInfoBar):
    def __init__(self, **kwargs):
        super().__init__(
            text = _('You are offline'),
            icon_name = 'network-offline-symbolic',
            message_type = Gtk.MessageType.WARNING,
            **kwargs
        )
        self.feedman = FeedsManager()
        self.feedman.connect(
            'feedmanager_online_changed',
            lambda caller, value: self.set_revealed(not value)
        )
        self.set_revealed(False)


class GFeedsSuggestionBar(GFeedsInfoBar):
    def __init__(self, **kwargs):
        super().__init__(
            text = _('Add a feed or import an OPML file'),
            icon_name = 'list-add-symbolic',
            **kwargs
        )
        self.feedman = FeedsManager()
        self.feedman.feeds.connect(
            'pop',
            lambda caller, obj: self.on_feeds_pop(obj)
        )
        self.feedman.connect(
            'feedmanager_refresh_end',
            lambda caller, obj: self.on_feeds_pop()
        )
        self.feedman.feeds.connect(
            'append',
            lambda caller, obj: self.on_feeds_append(obj)
        )
        self.set_revealed(False)

    def on_feeds_pop(self, deleted_feed=None):
        if len(self.feedman.feeds) == 0:
            self.set_revealed(True)

    def on_feeds_append(self, feed):
        self.set_revealed(False)
