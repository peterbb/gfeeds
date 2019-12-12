from gi.repository import Gtk


def separator_header_func(row, prev_row=None):
    if (
            prev_row != None and
            row.get_header() == None
    ):
        row.set_header(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        )
