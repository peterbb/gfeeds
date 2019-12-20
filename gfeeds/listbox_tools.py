from gi.repository import Gtk


def separator_header_func(row, prev_row=None):
    if (
            prev_row is not None and
            row.get_header() is None
    ):
        row.set_header(
            Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        )
