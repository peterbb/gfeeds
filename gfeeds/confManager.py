from .singleton import Singleton
from gi.repository import GObject, GLib, Gio
from pathlib import Path
from os.path import isfile, isdir
from os import makedirs, listdir
from os import environ as Env
import json
from datetime import timedelta

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
        # Signals down here don't have to do with the config
        'gfeeds_filter_changed': (
            GObject.SIGNAL_RUN_FIRST,
            None,
            (GObject.TYPE_PYOBJECT,)
        )
    }

class ConfManager(metaclass=Singleton):

    BASE_SCHEMA = {
        'feeds': [
        ],
        'dark_reader': False,
        'default_reader': False,
        'new_first': True,
        'windowsize': {
            'width': 350,
            'height': 650
        },
        'max_article_age_days': 30,
        'enable_js': False,
        'enable_csd': True,
        'use_rss_content': False,
        'max_refresh_threads': 2
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
            self.path = Path(f'{Env.get("XDG_CONFIG_HOME")}/org.gabmus.gnome-feeds.json')
            self.cache_path = Path(f'{Env.get("XDG_CACHE_HOME")}/gnome-feeds')
        else:
            self.path = Path(f'{Env.get("HOME")}/.config/gnome-feeds.json')
            self.cache_path = Path(f'{Env.get("HOME")}/.cache/gnome-feeds')
        self.thumbs_cache_path = f'{self.cache_path}/thumbnails/'

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
            except:
                self.conf = self.BASE_SCHEMA.copy()
                self.save_conf()
        else:
            self.conf = self.BASE_SCHEMA.copy()
            self.save_conf()

        for p in [self.cache_path, self.thumbs_cache_path]:
            if not isdir(p):
                makedirs(p)

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

    def save_conf(self):
        with open(self.path, 'w') as fd:
            fd.write(json.dumps(self.conf))
            fd.close()
