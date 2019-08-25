from gi.repository import Gtk
from .feeds_manager import FeedsManager

class GFeedsSuggestionBar(Gtk.Revealer):
    def __init__(self, text, icon_name = None, **kwargs):
        super().__init__(**kwargs)
        self.feedman = FeedsManager()
        self.text = text

        self.super_box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)
        self.super_box.get_style_context().add_class('frame')
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
        self.container_box.set_margin_top(12)
        self.container_box.set_margin_bottom(12)
        self.super_box.set_center_widget(self.container_box)
        self.add(self.super_box)

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

    def on_feeds_pop(self, deleted_feed=None):
        if len(self.feedman.feeds) == 0:
            self.set_reveal_child(True)

    def on_feeds_append(self, feed):
        self.set_reveal_child(False)
