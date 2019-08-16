import feedparser
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone
import pytz
from dateutil.parser import parse as dateparse
from dateutil.tz import gettz
from gettext import gettext as _
from .download_manager import download_raw, download_text
from .get_favicon import get_favicon
from os.path import isfile
from os import remove
from .confManager import ConfManager
from .sha import shasum
from PIL import Image
from .colorthief import ColorThief
import json

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
        self.pub_date = None # datetime.now(timezone.utc) # fallback to avoid errors
        self.parent_feed = parent_feed

        try:
            self.pub_date = dateparse(self.pub_date_str, tzinfos = {
                'UT': gettz('GMT'),
                'EST': -18000,
                'EDT': -14400,
                'CST': -21600,
                'CDT': -18000,
                'MST': -25200,
                'MDT': -21600,
                'PST': -28800,
                'PDT': -25200
            })
            if not self.pub_date.tzinfo:
                self.pub_date = pytz.UTC.localize(self.pub_date)
        except:
            print(_(
                'Error: unable to parse datetime {0} for feeditem {1}'
            ).format(self.pub_date_str, self))

    def __repr__(self):
        return f'FeedItem Object `{self.title}` from Feed {self.parent_feed.title}'

    def to_dict(self):
        return {
            'title': self.title,
            'link': self.link,
            'linkhash': shasum(self.link),
            'published': str(self.pub_date),
            'parent_feed': {
                'title': self.parent_feed.title,
                'link': self.parent_feed.link,
                'favicon_path': self.parent_feed.favicon_path
            }
        }

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def new_from_dict(cls, n_fi_dict):
        return cls(
            n_fi_dict,
            FakeFeed(n_fi_dict['parent_feed'])
        )

    @classmethod
    def new_from_json(cls, fi_json):
        return cls.new_from_dict(json.loads(fi_json))

class FakeFeed:
    def __init__(self, f_dict):
        self.title = f_dict.get('title', '')
        self.link = f_dict.get('link', '')
        self.favicon_path = f_dict.get('favicon_path', '')
        self.color = [0, 0, 0]
        if isfile(self.favicon_path):
            favicon = Image.open(self.favicon_path)
            if favicon.width != 32:
                favicon = favicon.resize((32, 32), Image.BILINEAR)
                favicon.save(self.favicon_path, 'PNG')
            self.color = ColorThief(favicon).get_color(quality=1)
            self.color = [c/255.0 for c in self.color]
            favicon.close()

    def __repr__(self):
        return f'FakeFeed Object `{self.title}`'

class Feed:
    def __init__(self, download_res):
        if not download_res:
            return None
        feedpath = download_res[0]
        with open(feedpath, 'r') as fd:
            self.fp_feed = feedparser.parse(fd.read())
            fd.close()

        self.confman = ConfManager()
        self.init_time = pytz.UTC.localize(datetime.utcnow())
        
        self.rss_link = download_res[1]
        self.title = self.fp_feed.feed.get('title', '')
        self.link = self.fp_feed.feed.get('link', '')
        self.description = self.fp_feed.feed.get('subtitle', self.link)
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
                self._resize_and_get_color(self.favicon_path)
            except:
                print(_(
                    'Error resizing favicon for feed {0}. ' \
                    'Probably not an image.\n' \
                    'Trying downloading favicon from an article.'
                ).format(self.title))
                try:
                    get_favicon(self.items[0].link, self.favicon_path)
                    self._resize_and_get_color(self.favicon_path)
                except:
                    print(_(
                        'Error resizing favicon from article for feed {0}.\n' \
                        'Deleting invalid favicon.'
                    ).format(self.title))
                    remove(self.favicon_path)


    def _resize_and_get_color(self, img_path):
        favicon = Image.open(img_path)
        if favicon.width != 32:
            favicon = favicon.resize((32, 32), Image.BILINEAR)
            favicon.save(self.favicon_path, 'PNG')
        self.color = ColorThief(favicon).get_color(quality=1)
        self.color = [c/255.0 for c in self.color]
        favicon.close()

    def __repr__(self):
        return f'Feed Object `{self.title}`; {len(self.items)} items'
