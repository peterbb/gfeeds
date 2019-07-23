from gettext import gettext as _
from gi.repository import Gtk, WebKit2
from subprocess import Popen

class GFeedsWebView(Gtk.Stack):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.set_hexpand(True)
        self.set_size_request(300, 500)

        self.filler_builder = Gtk.Builder.new_from_resource(
            '/org/gabmus/gnome-feeds/ui/webview_filler.glade'
        )

        self.webkitview_settings = WebKit2.Settings()
        self.webkitview_settings.set_enable_javascript(False)
        self.webkitview_settings.set_enable_smooth_scrolling(True)

        self.webkitview = WebKit2.WebView()
        self.webkitview.set_settings(self.webkitview_settings)

        self.fillerview = self.filler_builder.get_object('webview_filler_box')

        self.webkitview.set_hexpand(True)
        self.fillerview.set_hexpand(True)
        self.webkitview.set_size_request(300, 500)
        self.fillerview.set_size_request(300, 500)

        self.add_titled(self.webkitview, 'Web View', _('Web View'))
        self.add_titled(self.fillerview, 'Filler View', _('Filler View'))

    def load_uri(self, *args, **kwargs):
        self.set_visible_child(self.webkitview)
        self.webkitview.load_uri(*args, **kwargs)

    def open_externally(self, *args):
        target = self.webkitview.get_uri()
        if target:
            Popen(f'xdg-open {target}'.split(' '))
