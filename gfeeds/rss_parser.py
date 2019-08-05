import feedparser
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
from gettext import gettext as _
from .download_manager import download_raw
from .get_favicon import get_favicon
from os.path import isfile
from .confManager import ConfManager
from .sha import shasum
from PIL import Image
from .colorthief import ColorThief

class FeedItem:
    def __init__(self, fp_item, parent_feed):
        self.fp_item = fp_item

        self.title = self.fp_item.get('title', '')
        self.link = self.fp_item.get('link', '')
        # self.description = self.fp_item.get('description', '')
        self.pub_date_str = self.fp_item.get(
            'published',
            self.fp_item.get('updated', '')
        )
        self.pub_date = None
        self.parent_feed = parent_feed

        try:
            self.pub_date = parsedate_to_datetime(self.pub_date_str)
        except:
            try:
                if self.pub_date_str[-1].lower() == 'z':
                    self.pub_date_str = self.pub_date_str[:-1]+'+00:00'
                self.pub_date = datetime.fromisoformat(self.pub_date_str)
            except:
                print(_('Error: unable to parse datetime'))

    def __repr__(self):
        return f'FeedItem Object `{self.title}` from Feed {self.parent_feed.title}'


class Feed:
    def __init__(self, download_res):
        if not download_res:
            return None
        feedpath = download_res[0]
        with open(feedpath, 'r') as fd:
            self.fp_feed = feedparser.parse(fd.read())
            fd.close()

        self.confman = ConfManager()
        self.init_time = datetime.now(timezone.utc)
        
        self.rss_link = download_res[1]
        self.title = self.fp_feed.feed.get('title', '')
        self.link = self.fp_feed.feed.get('link', '')
        self.description = self.fp_feed.feed.get('subtitle', '')
        # self.language = self.fp_feed.get('', '')
        self.image_url = self.fp_feed.get('image', {'href': ''})['href']
        self.items = []
        for entry in self.fp_feed.get('entries', []):
            n_item = FeedItem(entry, self)
            item_age = self.init_time - n_item.pub_date
            if item_age < self.confman.max_article_age:
                self.items.append(n_item)
        # self.items = [FeedItem(x, self) for x in self.fp_feed.get('entries', [])]
        self.color = [0, 0, 0]

        if not self.title:
            self.title = self.link
            if not self.title:
                self.title = self.rss_link

        self.favicon_path = self.confman.thumbs_cache_path+'/'+shasum(self.link)+'.png'
        if not isfile(self.favicon_path):
            if self.image_url:
                download_raw(self.image_url, self.favicon_path)
            else:
                try:
                    get_favicon(self.link, self.favicon_path)
                    if not isfile(self.favicon_path):
                        get_favicon(self.items[0].link, self.favicon_path)
                except:
                    print('No favicon')
        if isfile(self.favicon_path):
            try:
                favicon = Image.open(self.favicon_path)
                if favicon.width != 32:
                    favicon = favicon.resize((32, 32), Image.BILINEAR)
                    favicon.save(self.favicon_path, 'PNG')
                self.color = ColorThief(favicon).get_color(quality=1)
                self.color = [c/255.0 for c in self.color]
                favicon.close()
            except:
                print(_('Error resizing favicon for feed {0}').format(self.title))


    def __repr__(self):
        return f'Feed Object `{self.title}`; {len(self.items)} items'
