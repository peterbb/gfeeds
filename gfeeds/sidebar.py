from gi.repository import Gtk, Pango, Gdk
from xml.sax.saxutils import escape
from .confManager import ConfManager
import cairo

class GFeedsSidebarRow(Gtk.ListBoxRow):
    def __init__(self, feeditem, **kwargs):
        super().__init__(**kwargs)
        self.get_style_context().add_class('activatable')
        self.feeditem = feeditem
        self.super_box = Gtk.Box(orientation = Gtk.Orientation.HORIZONTAL)
        self.colored_box = Gtk.DrawingArea()
        self.colored_box.connect('draw', self.draw_color)
        self.colored_box.set_size_request(8, 20)
        self.colored_box.set_margin_right(6)

        self.title_label = Gtk.Label(
            f'<big><b>{escape(self.feeditem.title)}</b></big>'
        )
        self.origin_label = Gtk.Label(
            f'<i>{escape(self.feeditem.parent_feed.title)}</i>'
        )
        self.origin_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.date_label = Gtk.Label(
            (self.feeditem.pub_date).strftime('%Y %B %d, %H:%M')
        )
        self.icon = Gtk.Image.new_from_file(
            self.feeditem.parent_feed.favicon_path
        )
        self.super_box.pack_start(self.colored_box, False, False, 0)
        self.super_box.pack_start(self.icon, False, False, 6)
        self.box = Gtk.Box(orientation = Gtk.Orientation.VERTICAL)

        for l in [self.title_label, self.origin_label, self.date_label]:
            l.set_use_markup(True)
            l.set_line_wrap(True)
            l.set_hexpand(False)
            if l == self.date_label:
                l.set_halign(Gtk.Align.END)
                l.set_xalign(1)
            else:
                l.set_halign(Gtk.Align.START)
                l.set_xalign(0)
            self.box.pack_start(l, False, False, 3)

        self.super_box.pack_start(self.box, True, True, 6)
        self.add(self.super_box)

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
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)

        self.scrolled_win = GFeedsSidebarScrolledWin(self)
        self.listbox = self.scrolled_win.listbox
        self.empty = self.scrolled_win.listbox.empty
        self.populate = self.scrolled_win.listbox.populate
        self.select_next_article = self.scrolled_win.select_next_article
        self.select_prev_article = self.scrolled_win.select_prev_article

        self.filler_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/sidebar_filler.glade'
        )
        self.filler_view = self.filler_builder.get_object('sidebar_filler_box')

        self.add(self.filler_view)
        self.add(self.scrolled_win)
        self.set_size_request(300, 500)
        self.set_visible_child(self.filler_view)

    def set_main_visible(self, state):
        self.set_visible_child(
            self.scrolled_win if state else self.filler_view
        )
