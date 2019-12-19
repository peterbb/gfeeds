from gi.repository import Gtk
from gfeeds.confManager import ConfManager


class InitialsIcon(Gtk.Bin):
    confman = ConfManager()

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.label = Gtk.Label()
        namesplit = self.name.split()
        if len(namesplit) >= 2:
            self.initials = f'{namesplit[0][0]}{namesplit[1][0]}'.upper()
        else:
            self.initials = f'{self.name[0]}{self.name[1]}'.upper()
        self.icon_overlay = Gtk.Overlay()
        image = Gtk.Image.new_from_icon_name(
            'circle-filled-symbolic', Gtk.IconSize.INVALID
        )
        image.set_pixel_size(32)
        self.label.set_markup(
            '<span fgcolor="#{0}" weight="semibold">{1}</span>'.format(
                InitialsIcon.confman.get_background_color(),
                self.initials
            )
        )
        self.icon_overlay.add(image)
        self.icon_overlay.add_overlay(self.label)

        self.add(self.icon_overlay)
