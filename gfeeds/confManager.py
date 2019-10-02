from .singleton import Singleton
from gi.repository import GObject, Gio
from pathlib import Path
from os.path import isfile, isdir
from os import makedirs
from os import environ as Env
import json
from datetime import timedelta
from .signaler_list import SignalerList

class ConfManagerSignaler(GObject.Object):
    __gsignals__ = {
        'gfeeds_new_first_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'gfeeds_repopulation_required': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'gfeeds_webview_settings_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'gfeeds_enable_csd_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'gfeeds_show_read_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'gfeeds_colored_border_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        'gfeeds_full_article_title_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (str,)
        ),
        # Signals down here don't have to do with the config
        'gfeeds_filter_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (GObject.TYPE_PYOBJECT,)
        )
    }

class ConfManager(metaclass=Singleton):

    BASE_SCHEMA = {
        'feeds': {},
        'dark_reader': False,
        'new_first': True,
        'windowsize': {
            'width': 350,
            'height': 650
        },
        'max_article_age_days': 30,
        'enable_js': False,
        'enable_csd': True,
        'max_refresh_threads': 2,
        'saved_items': {},
        'read_items': [],
        'show_read_items': True,
        'colored_border': True,
        'full_article_title': True,
        'default_view': 'webview' # valid values: 'webview', 'reader', 'rsscont'
    }

    def __init__(self):
        self.signaler = ConfManagerSignaler()
        self.emit = self.signaler.emit
        self.connect = self.signaler.connect

        # check if inside flatpak sandbox
        self.is_flatpak = False
        if 'XDG_RUNTIME_DIR' in Env.keys():
            if isfile(f'{Env["XDG_RUNTIME_DIR"]}/flatpak-info'):
                self.is_flatpak = True

        if self.is_flatpak:
            self.path = Path(f'{Env.get("XDG_CONFIG_HOME")}/org.gabmus.gfeeds.json')
            self.cache_path = Path(f'{Env.get("XDG_CACHE_HOME")}/org.gabmus.gfeeds')
        else:
            self.path = Path(f'{Env.get("HOME")}/.config/org.gabmus.gfeeds.json')
            self.cache_path = Path(f'{Env.get("HOME")}/.cache/org.gabmus.gfeeds')
        self.thumbs_cache_path = f'{self.cache_path}/thumbnails/'
        self.saved_cache_path = f'{self.cache_path}/saved_articles'

        self.conf = None
        if isfile(self.path):
            try:
                with open(self.path) as fd:
                    self.conf = json.loads(fd.read())
                    fd.close()
                # verify that the file has all of the schema keys
                for k in self.BASE_SCHEMA.keys():
                    if not k in self.conf.keys():
                        if type(self.BASE_SCHEMA[k]) in [list, dict]:
                            self.conf[k] = self.BASE_SCHEMA[k].copy()
                        else:
                            self.conf[k] = self.BASE_SCHEMA[k]
                if type(self.conf['feeds']) == list:
                    n_feeds = {}
                    for o_feed in self.conf['feeds']:
                        n_feeds[o_feed] = {}
                    self.conf['feeds'] = n_feeds
                    self.save_conf()
            except:
                self.conf = self.BASE_SCHEMA.copy()
                self.save_conf()
        else:
            self.conf = self.BASE_SCHEMA.copy()
            self.save_conf()

        for p in [
            self.cache_path,
            self.thumbs_cache_path,
            self.saved_cache_path
        ]:
            if not isdir(p):
                makedirs(p)

        self.read_feeds_items = SignalerList(self.conf['read_items'])
        self.read_feeds_items.connect(
            'append', self.dump_read_items_to_conf
        )
        self.read_feeds_items.connect(
            'pop', self.dump_read_items_to_conf
        )

        bl_gsettings = Gio.Settings.new('org.gnome.desktop.wm.preferences')
        bl = bl_gsettings.get_value('button-layout').get_string()
        self.wm_decoration_on_left = (
            'close:' in bl or
            'maximize:' in bl or
            'minimize:' in bl
        )


    @property
    def max_article_age(self):
        return timedelta(days=self.conf['max_article_age_days'])

    def dump_read_items_to_conf(self, *args):
        self.conf['read_items'] = self.read_feeds_items.get_list()

    def save_conf(self, *args):
        with open(self.path, 'w') as fd:
            fd.write(json.dumps(self.conf))
            fd.close()
