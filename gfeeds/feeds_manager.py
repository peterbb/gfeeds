from gettext import gettext as _
from gi.repository import GLib, GObject
from .singleton import Singleton
from .confManager import ConfManager
from .rss_parser import Feed, FeedItem
import threading
from .download_manager import download_feed
from .signaler_list import SignalerList
from .test_connection import is_online
from .thread_pool import ThreadPool

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
        'feedmanager_online_changed': (
            GObject.SIGNAL_RUN_LAST,
            None,
            (bool,)
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

        self.errors = []

    def populate_saved_feeds_items(self):
        self.saved_feeds_items.empty()
        for si in self.confman.conf['saved_items'].values():
            self.saved_feeds_items.append(
                FeedItem.new_from_dict(si)
            )

    def _add_feed_async_worker(self, uri, refresh=False, get_cached=False):
        if not refresh:
            if not 'http://' in uri and not 'https://' in uri:
                uri = 'http://' + uri
            if uri in self.confman.conf['feeds'].keys():
                print(_('Feed {0} exists already, skipping').format(uri))
                return
            self.confman.conf['feeds'][uri] = {}
            self.confman.save_conf()
        download_res = download_feed(uri, get_cached=get_cached)
        if get_cached and download_res[0] == 'not_cached':
            return
        n_feed = Feed(download_res)
        if n_feed.is_null:
            self.errors.append(n_feed.error)
            if uri in self.confman.conf['feeds'].keys():
                self.confman.conf['feeds'].pop(uri)
                self.confman.save_conf()
        else:
            GLib.idle_add(
                self.feeds.append, n_feed
            )
            for n_feed_item in n_feed.items:
                GLib.idle_add(
                    self.feeds_items.append, n_feed_item
                )
        if not refresh:
            GLib.idle_add(
                self.emit, 'feedmanager_refresh_end', ''
            )

    def refresh(self, *args, get_cached=False):
        self.emit('feedmanager_refresh_start', '')
        self.errors = []
        if is_online():
            self.emit('feedmanager_online_changed', True)
        else:
            self.emit('feedmanager_online_changed', False)
            get_cached = True
            # self.emit('feedmanager_refresh_end', '')
            # return
        self.populate_saved_feeds_items()
        self.feeds.empty()
        self.feeds_items.empty()
        tp = ThreadPool(
            self.confman.conf['max_refresh_threads'],
            self._add_feed_async_worker,
            [(f_link, True, get_cached) for f_link in self.confman.conf['feeds'].keys()],
            self.emit,
            ('feedmanager_refresh_end', '')
        )
        tp.start()

    def add_feed(self, uri, is_new=False):
        if is_new and uri in self.confman.conf['feeds'].keys():
            return False
        self.emit('feedmanager_refresh_start', '')
        self.errors = []
        t = threading.Thread(
            group=None,
            target=self._add_feed_async_worker,
            name=None,
            args=(uri,)
        )
        t.start()
        return True

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
            
