from gettext import gettext as _
from gi.repository import Gtk, GLib, GObject
from .singleton import Singleton
from .confManager import ConfManager
from .rss_parser import Feed, FeedItem
import threading
from .download_manager import download_feed
from .signaler_list import SignalerList

class FeedsManagerSignaler(GObject.Object):
    __gsignals__ = {
        'feedmanager_refresh_start': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (str,)
        ),
        'feedmanager_refresh_end': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (str,)
        ),
    }

class FeedsManager(metaclass=Singleton):
    def __init__(self):
        self.confman = ConfManager()
        self.confman.connect(
            'gfeeds_repopulation_required',
            self.refresh
        )
        self.signaler = FeedsManagerSignaler()
        self.emit = self.signaler.emit
        self.connect = self.signaler.connect

        self.feeds = SignalerList()
        self.feeds_items = SignalerList()
        self.saved_feeds_items = SignalerList()

    def populate_saved_feeds_items(self):
        self.saved_feeds_items.empty()
        for si in self.confman.conf['saved_items'].values():
            self.saved_feeds_items.append(
                FeedItem.new_from_dict(si)
            )

    def _add_feed_async_worker(self, uri, refresh = False):
        if not refresh:
            if not 'http://' in uri and not 'https://' in uri:
                uri = 'http://' + uri
            if uri in self.confman.conf['feeds'].keys():
                print(_('Feed {0} exists already, skipping').format(uri))
                return
            self.confman.conf['feeds'][uri] = {}
            self.confman.save_conf()
        n_feed = Feed(download_feed(uri))
        if n_feed.is_null:
            if uri in self.confman.conf['feeds'].keys():
                self.confman.conf['feeds'].pop(uri)
                self.confman.save_conf()
            return
        GLib.idle_add(
            self.feeds.append, n_feed,
            priority = GLib.PRIORITY_DEFAULT_IDLE
        )
        for n_feed_item in n_feed.items:
            GLib.idle_add(
                self.feeds_items.append, n_feed_item,
                priority = GLib.PRIORITY_DEFAULT_IDLE
            )

    def refresh(self, *args):
        self.emit('feedmanager_refresh_start', '')
        self.populate_saved_feeds_items()
        self.feeds.empty()
        self.feeds_items.empty()
        threads_pool = []
        threads_alive = []
        MAX_THREADS = self.confman.conf['max_refresh_threads']
        for f_link in self.confman.conf['feeds'].keys():
            t = threading.Thread(
                group = None,
                target = self._add_feed_async_worker,
                name = None,
                args = (f_link, True)
            )
            threads_pool.append(t)
        while len(threads_pool) > 0:
            if len(threads_alive) < MAX_THREADS:
                t = threads_pool.pop(0)
                t.start()
                threads_alive.append(t)
            threads_to_rem = []
            for t in threads_alive:
                if not t.is_alive():
                    threads_to_rem.append(t)
            for t in threads_to_rem:
                threads_alive.pop(
                    threads_alive.index(t)
                )
            while t.is_alive():
                while Gtk.events_pending():
                    Gtk.main_iteration()

        self.emit('feedmanager_refresh_end', '')

    def add_feed(self, uri):
        self.emit('feedmanager_refresh_start', '')

        t = threading.Thread(
            group = None,
            target = self._add_feed_async_worker,
            name = None,
            args = (uri,)
        )
        t.start()
        while t.is_alive():
            while Gtk.events_pending():
                Gtk.main_iteration()

        self.emit('feedmanager_refresh_end', '')

    def delete_feeds(self, targets, *args):
        if type(targets) != list:
            if type(targets) == Feed:
                targets = [targets]
            else:
                raise TypeError('delete_feed: targets must be list or Feed')
        for f in targets:
            for fi in f.items:
                self.feeds_items.pop(
                    self.feeds_items.index(fi)
                )
            self.feeds.pop(
                self.feeds.index(f)
            )
            self.confman.conf['feeds'].pop(
                f.rss_link
            )
        self.confman.save_conf()
            
