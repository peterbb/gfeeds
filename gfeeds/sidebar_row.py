from gi.repository import Gtk, GLib, Pango
from .colored_box import GFeedsColoredBox
from .confManager import ConfManager
from .relative_day_formatter import get_date_format
from .rss_parser import FeedItem
from .sidebar_row_popover import RowPopover
from datetime import timezone
from os.path import isfile
import cairo


class GFeedsSidebarRow(Gtk.ListBoxRow):
    def __init__(self, feeditem, is_saved = False, **kwargs):
        super().__init__(**kwargs)
        self.is_saved = is_saved
        self.get_style_context().add_class('activatable')
        self.feeditem = feeditem
        self.confman = ConfManager()

        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/sidebar_listbox_row.glade'
        )
        self.container_box = self.builder.get_object('container_box')
        self.colored_box = GFeedsColoredBox(self.feeditem.parent_feed.color)
        self.builder.get_object('colored_box_container').add(self.colored_box)
        self.on_show_colored_border_changed()
        self.confman.connect(
            'gfeeds_colored_border_changed',
            self.on_show_colored_border_changed
        )
        self.title_label = self.builder.get_object('title_label')
        self.title_label.set_text(self.feeditem.title)
        self.confman.connect(
            'gfeeds_full_article_title_changed',
            self.on_full_article_title_changed
        )
        self.on_full_article_title_changed()
        self.origin_label = self.builder.get_object('origin_label')
        self.origin_label.set_text(self.feeditem.parent_feed.title)

        self.icon = self.builder.get_object('icon')
        if isfile(self.feeditem.parent_feed.favicon_path):
            self.icon.set_from_file(
                self.feeditem.parent_feed.favicon_path
            )

        # Date & time stuff is long
        self.date_label = self.builder.get_object('date_label')
        tz_sec_offset = self.feeditem.pub_date.utcoffset().total_seconds()
        glibtz = GLib.TimeZone(
            (
                '{0}{1}:{2}'.format(
                    '+' if tz_sec_offset >= 0 else '',
                    format(int(tz_sec_offset/3600), '02'),
                    format(int(
                        (tz_sec_offset - (int(tz_sec_offset/3600)*3600))/60
                    ), '02'),
                )
            ) or '+00:00'
        )
        self.datestr = GLib.DateTime(
            glibtz,
            self.feeditem.pub_date.year,
            self.feeditem.pub_date.month,
            self.feeditem.pub_date.day,
            self.feeditem.pub_date.hour,
            self.feeditem.pub_date.minute,
            self.feeditem.pub_date.second
        ).to_local().format(get_date_format(self.feeditem.pub_date))
        self.date_label.set_text(
            self.datestr
        )

        self.popover = RowPopover(self)

        self.add(self.container_box)
        self.set_read()

    def on_full_article_title_changed(self, *args):
        self.title_label.set_ellipsize(
            Pango.EllipsizeMode.NONE if self.confman.conf['full_article_title']
            else Pango.EllipsizeMode.END
        )

    def on_show_colored_border_changed(self, *args):
        if self.confman.conf['colored_border']:
            self.colored_box.show()
            self.colored_box.set_no_show_all(False)
        else:
            self.colored_box.hide()
            self.colored_box.set_no_show_all(True)

    def set_read(self, read = None):
        if read != None:
            self.feeditem.set_read(read)
        if self.feeditem.read:
            self.set_dim(True)
        else:
            self.set_dim(False)

    def set_dim(self, state):
        for w in [
            self.colored_box,
            self.title_label,
            self.icon
        ]:
            if state:
                w.get_style_context().add_class('dim-label')
            else:
                w.get_style_context().remove_class('dim-label')
