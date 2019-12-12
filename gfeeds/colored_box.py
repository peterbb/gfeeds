from gi.repository import Gtk
from cairo import LineJoin


class GFeedsColoredBox(Gtk.DrawingArea):
    def __init__(self, color, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color = color
        self.connect('draw', self.draw_color)
        self.set_size_request(12, -1)
        self.set_vexpand(True)

    def draw_color(self, da, ctx):
        ctx.set_source_rgb(
            self.color[0],
            self.color[1],
            self.color[2],
        )
        ctx.set_line_width(20 / 4)
        ctx.set_tolerance(0.1)
        ctx.set_line_join(LineJoin.BEVEL)
        ctx.save()
        ctx.new_path()
        ctx.move_to(0, 0)
        ctx.rel_line_to(12, 0)
        ctx.rel_line_to(0, 800)
        ctx.rel_line_to(-12, 0)
        ctx.rel_line_to(0, -800)
        # ctx.close_path()
        ctx.fill()
        ctx.restore()

        ctx.close_path()
