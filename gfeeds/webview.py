from gettext import gettext as _
from gi.repository import Gtk, WebKit2, GObject
from subprocess import Popen
from .build_reader_html import build_reader_html

class GFeedsWebView(Gtk.Stack):
    __gsignals__ = {
        'gfeeds_webview_load_end': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (str,)
        ),
        'gfeeds_webview_load_start': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        )
    }
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
        self.webkitview_settings.set_enable_page_cache(True)

        self.webkitview = WebKit2.WebView()
        self.webkitview.set_settings(self.webkitview_settings)
        self.webkitview.connect('load-changed', self.on_load_changed)

        self.fillerview = self.filler_builder.get_object('webview_filler_box')

        self.webkitview.set_hexpand(True)
        self.fillerview.set_hexpand(True)
        self.webkitview.set_size_request(300, 500)
        self.fillerview.set_size_request(300, 500)

        self.add_titled(self.webkitview, 'Web View', _('Web View'))
        self.add_titled(self.fillerview, 'Filler View', _('Filler View'))

        self.new_page_loaded = False
        self.uri = ''
        self.html = None

    def load_uri(self, uri, *args, **kwargs):
        self.set_visible_child(self.webkitview)
        self.uri = uri
        self.webkitview.load_uri(uri, *args, **kwargs)
        self.on_load_start()

    def open_externally(self, *args):
        target = self.webkitview.get_uri()
        if target:
            Popen(f'xdg-open {target}'.split(' '))

    def on_load_start(self, *args):
        self.new_page_loaded = True
        self.emit('gfeeds_webview_load_start', '')

    def on_load_changed(self, webview, event):
        if self.new_page_loaded and event == WebKit2.LoadEvent.FINISHED:
            self.emit('gfeeds_webview_load_end', '')
            self.new_page_loaded = False
            resource = webview.get_main_resource()
            resource.get_data(None, self._get_data_cb, None)

    def set_enable_reader_mode(self, togglebtn):
        print('RECEIVED')
        state = togglebtn.get_active()
        if state:
            self.webkitview.load_html(build_reader_html(self.html))
        else:
            self.webkitview.load_uri(self.uri)

    def _get_data_cb(self, resource, result, user_data=None):
        self.html = resource.get_data_finish(result)
