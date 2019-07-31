from .singleton import Singleton
from gi.repository import GObject, GLib
from pathlib import Path
from os.path import isfile, isdir
from os import makedirs, listdir
from os import environ as Env
import json

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
        )
    }

class ConfManager(metaclass=Singleton):

    BASE_SCHEMA = {
        'feeds': [
        ],
        'dark_reader': False,
        'new_first': True,
        'windowsize': {
            'width': 350,
            'height': 650
        }
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

    def save_conf(self):
        with open(self.path, 'w') as fd:
            fd.write(json.dumps(self.conf))
            fd.close()
