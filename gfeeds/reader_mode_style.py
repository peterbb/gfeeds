from gi.repository import Gio

CSS = Gio.resources_lookup_data(
    '/org/gabmus/gfeeds/reader_mode_style.css',
    Gio.ResourceLookupFlags.NONE
).get_data().decode()
DARK_MODE_CSS = Gio.resources_lookup_data(
    '/org/gabmus/gfeeds/reader_mode_dark_style.css',
    Gio.ResourceLookupFlags.NONE
).get_data().decode()

print('CSS HERE!\n'*100)
print(CSS)
