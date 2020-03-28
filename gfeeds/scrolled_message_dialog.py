from gi.repository import Gtk


class ScrolledMessageDialog(Gtk.MessageDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gfeeds/ui/scrolled_label.glade'
        )
        self.scrolled_win = self.builder.get_object('scrolled_win')
        self.label = self.builder.get_object('label')

        self.get_content_area().pack_start(self.scrolled_win, True, True, 0)
        self.get_content_area().set_spacing(0)
        self.get_message_area().set_spacing(0)
        self.get_message_area().get_children()[0].set_margin_bottom(20)

    def format_secondary_markup(self, message):
        self.label.set_markup(message)
