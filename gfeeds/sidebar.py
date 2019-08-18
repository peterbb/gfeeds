from gi.repository import Gtk, Gdk, GLib
from datetime import timezone
from os.path import isfile
from os import remove
import cairo
import threading
from .confManager import ConfManager
from .feeds_manager import FeedsManager
from .rss_parser import FeedItem
from .download_manager import download_raw
from gettext import gettext as _


class RowPopover(Gtk.Popover):
    def __init__(self, parent, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.feedman = FeedsManager()
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/article_right_click_popover_content.glade'
        )
        self.container_box = self.builder.get_object('container_box')
        # self.set_size_request(270, 150)
        self.parent = parent

        # self.title_label = self.builder.get_object('title_label')
        # self.title_label.set_text(self.parent.feeditem.title)

        self.read_unread_btn = self.builder.get_object('read_unread_btn')
        self.read_unread_btn.connect('clicked', self.on_read_unread_clicked)

        self.save_btn = self.builder.get_object('save_btn')
        self.save_btn.set_active(
            self.parent.feeditem.link in self.confman.conf['saved_items'].keys()
        )
        self.save_btn_handler_id = self.save_btn.connect(
            'toggled', self.on_save_toggled
        )

        self.set_modal(True)
        self.set_relative_to(self.parent)
        self.add(self.container_box)
        self.read = not False # TODO: get from feeditem?
        self.on_read_unread_clicked(self.read_unread_btn)

    def on_read_unread_clicked(self, btn):
        if self.read:
            self.read = False
            btn.get_children()[0].set_from_icon_name(
                'eye-open-negative-filled-symbolic',
                Gtk.IconSize.BUTTON
            )
            btn.set_tooltip_text(_(
                'Mark as read'
            ))
        else:
            self.read = True
            btn.get_children()[0].set_from_icon_name(
                'eye-not-looking-symbolic',
                Gtk.IconSize.BUTTON
            )
            btn.set_tooltip_text(_(
                'Mark as unread'
            ))

    def on_save_toggled(self, togglebtn):
        togglebtn.set_sensitive(False)
        if togglebtn.get_active():
            fi_dict = self.parent.feeditem.to_dict()
            t = threading.Thread(
                group = None,
                target = download_raw,
                name = None,
                args = (
                    fi_dict['link'],
                    self.confman.saved_cache_path + '/' + fi_dict['linkhash']
                )
            )
            t.start()
            while t.is_alive():
                while Gtk.events_pending():
                    Gtk.main_iteration()
            self.confman.conf['saved_items'][self.parent.feeditem.link] = fi_dict
        else:
            todel_fi_dict = self.confman.conf['saved_items'].pop(
                self.parent.feeditem.link
            )
            remove(
                self.confman.saved_cache_path + '/' + todel_fi_dict['linkhash']
            )
            # parent.is_saved means "the row that spawned the popover is from
            # the *Saved* section"
            if self.parent.is_saved:
                parent_stack = self.parent.get_parent().get_parent(
                    ).get_parent().get_parent()
                parent_stack.on_saved_item_deleted(todel_fi_dict['link'])
        self.confman.save_conf()
        self.feedman.populate_saved_feeds_items()
        togglebtn.set_sensitive(True)

class GFeedsSidebarRow(Gtk.ListBoxRow):
    def __init__(self, feeditem, is_saved = False, **kwargs):
        super().__init__(**kwargs)
        self.is_saved = is_saved
        self.get_style_context().add_class('activatable')
        self.feeditem = feeditem

        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/sidebar_listbox_row.glade'
        )
        self.container_box = self.builder.get_object('container_box')
        self.colored_box = self.builder.get_object('drawing_area')
        self.colored_box.connect('draw', self.draw_color)
        self.title_label = self.builder.get_object('title_label')
        self.title_label.set_text(self.feeditem.title)
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
        ).to_local().format('%c')
        self.date_label.set_text(
            self.datestr
        )

        self.popover = RowPopover(self)

        self.add(self.container_box)

    def draw_color(self, da, ctx):
        ctx.set_source_rgb(
            self.feeditem.parent_feed.color[0],
            self.feeditem.parent_feed.color[1],
            self.feeditem.parent_feed.color[2],
        )
        ctx.set_line_width(20 / 4)
        ctx.set_tolerance(0.1)
        ctx.set_line_join(cairo.LINE_JOIN_BEVEL)
        ctx.save()
        ctx.new_path()
        ctx.move_to(0, 0)
        ctx.rel_line_to(8,0)
        ctx.rel_line_to(0,800)
        ctx.rel_line_to(-8,0)
        ctx.rel_line_to(0,-800)
        # ctx.close_path()
        ctx.fill()
        ctx.restore()

        ctx.close_path()

class GFeedsSidebarListBox(Gtk.ListBox):
    def __init__(self, parent_stack, **kwargs):
        super().__init__(**kwargs)
        self.confman = ConfManager()
        self.parent_stack = parent_stack

        self.set_sort_from_confman()
        self.confman.connect(
            'gfeeds_new_first_changed',
            self.set_sort_from_confman
        )
        self.selected_feed = None
        self.set_filter_func(self.gfeeds_sidebar_filter_func, None, False)
        self.confman.connect(
            'gfeeds_filter_changed',
            self.change_filter
        )

        # longpress & right click
        self.longpress = Gtk.GestureLongPress.new(self)
        self.longpress.set_propagation_phase(Gtk.PropagationPhase.TARGET)
        self.longpress.set_touch_only(False)
        self.longpress.connect(
            'pressed',
            self.on_right_click,
            self
        )
        self.connect(
            'button-press-event',
            self.on_key_press_event
        )

    def on_right_click(self, e_or_g, x, y, *args):
        row = self.get_row_at_y(y)
        if row:
            row.popover.popup()

    def on_key_press_event(self, what, event):
        if event.type == Gdk.EventType.BUTTON_PRESS and event.button == 3: # right click
            self.on_right_click(event, event.x, event.y)

    def change_filter(self, caller, n_filter):
        self.selected_feed = n_filter
        self.set_filter_func(self.gfeeds_sidebar_filter_func, None, False)

    def gfeeds_sidebar_filter_func(self, row, data, notify_destroy):
        if not self.selected_feed:
            return True
        else:
            return row.feeditem.parent_feed == self.selected_feed

    def set_sort_from_confman(self, *args):
        if self.confman.conf['new_first']:
            self.set_sort_func(self.gfeeds_sort_new_first_func, None, False)
        else:
            self.set_sort_func(self.gfeeds_sort_old_first_func, None, False)

    def add_new_items(self, feeditems_l):
        self.parent_stack.set_main_visible(True)
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


class GFeedsSidebarScrolledWin(Gtk.ScrolledWindow):
    def __init__(self, parent_stack, **kwargs):
        super().__init__(**kwargs)
        self.parent_stack = parent_stack
        self.listbox = GFeedsSidebarListBox(self.parent_stack)
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

class GFeedsSidebar(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.feedman = FeedsManager()
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.scrolled_win = GFeedsSidebarScrolledWin(self)
        self.listbox = self.scrolled_win.listbox
        self.empty = self.scrolled_win.listbox.empty
        self.populate = self.scrolled_win.listbox.populate

        self.filler_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/sidebar_filler.glade'
        )
        self.filler_view = self.filler_builder.get_object('sidebar_filler_box')

        self.saved_items_scrolled_win = GFeedsSidebarScrolledWin(self)
        self.saved_items_listbox = self.saved_items_scrolled_win.listbox

        self.add(self.filler_view)
        self.add_titled(self.scrolled_win, 'Feed', _('Feed'))
        self.child_set_property(
            self.scrolled_win,
            'icon-name',
            'application-rss+xml-symbolic'
        )
        self.add_titled(self.saved_items_scrolled_win, 'Saved', _('Saved'))
        self.child_set_property(
            self.saved_items_scrolled_win,
            'icon-name',
            'emblem-favorite-symbolic'
        )
        self.set_size_request(300, 500)
        self.set_visible_child(self.filler_view)

        self.feedman.feeds_items.connect(
            'feeds_items_pop',
            lambda caller, obj: self.on_feeds_items_pop(obj)
        )
        self.feedman.feeds_items.connect(
            'feeds_items_append',
            lambda caller, obj: self.on_feeds_items_append(obj)
        )
        self.feedman.feeds.connect(
            'feeds_pop',
            lambda caller, obj: self.on_feeds_pop(obj)
        )
        self.feedman.feeds.connect(
            'feeds_append',
            lambda caller, obj: self.on_feeds_append(obj)
        )
        self.feedman.feeds_items.connect(
            'feeds_items_empty',
            lambda *args: self.listbox.empty()
        )

        self.feedman.saved_feeds_items.connect(
            'saved_feeds_items_empty',
            lambda *args: self.saved_items_listbox.empty()
        )
        self.feedman.saved_feeds_items.connect(
            'saved_feeds_items_append',
            lambda caller, obj: self.on_saved_feeds_items_append(obj)
        )

    def on_saved_item_deleted(self, deleted_link):
        for row in self.listbox.get_children():
            if row.feeditem.link == deleted_link:
                with row.popover.save_btn.handler_block(
                    row.popover.save_btn_handler_id
                ):
                    row.popover.save_btn.set_active(False)
                break

    def select_next_article(self, *args):
        visible_child = self.get_visible_child()
        if visible_child != self.filler_view:
            visible_child.select_next_article

    def select_prev_article(self, *args):
        visible_child = self.get_visible_child()
        if visible_child != self.filler_view:
            visible_child.select_prev_article

    def on_feeds_append(self, feed):
        if self.get_visible_child() == self.filler_view:
            self.set_visible_child(self.scrolled_win)

    def on_feeds_pop(self, feed):
        if len(self.feedman.feeds) == 0:
            self.set_visible_child(self.filler_view)

    def on_feeds_items_pop(self, feeditem):
        for row in self.listbox.get_children():
            if row.feeditem == feeditem:
                self.listbox.remove(row)
                break

    def on_feeds_items_append(self, feeditem):
        n_row = GFeedsSidebarRow(feeditem)
        self.listbox.add(n_row)
        n_row.show_all()

    def on_saved_feeds_items_append(self, feeditem):
        n_row = GFeedsSidebarRow(feeditem, is_saved = True)
        self.saved_items_listbox.add(n_row)
        n_row.show_all()

    def on_saved_feeds_items_pop(self, feeditem):
        for row in self.saved_items_listbox.get_children():
            if row.feeditem == feeditem:
                self.listbox.remove(row)
                break
