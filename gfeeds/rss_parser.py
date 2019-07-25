from lxml import etree, objectify
from email.utils import parsedate_to_datetime
from datetime import datetime
from gettext import gettext as _
from .download_manager import download, download_raw
from .get_favicon import get_favicon
from os.path import isfile
from .confManager import ConfManager
from .sha import shasum
from PIL import Image

"""
quick XML parsing notes

<?xml version="1.0"?>               IGNORE THIS
<rss version="2.0">                 THIS IS THE ROOT
    <channel>                       THIS IS ROOT'S 0th AND ONLY CHILD
        <title>Phoronix</title>
        <link>https://www.phoronix.com/</link>
        <description>Linux Hardware Reviews &amp; News</description>
        <language>en-us</language>
        <item>
            <title>RadeonSI Gallium3D Driver Adds Navi Wave32 Support</title>
            <link>http://www.phoronix.com/scan.php?page=news_item&amp;px=RadeonSI-Wave32-Lands</link>
            <guid>http://www.phoronix.com/scan.php?page=news_item&amp;px=RadeonSI-Wave32-Lands</guid>
            <description>One of the new features to the RDNA architecture with Navi is support for single cycle issue Wave32 execution on SIMD32. Up to now the RadeonSI code was using just Wave64 but now there is support in this AMD open-source Linux OpenGL driver for Wave32...</description>
            <pubDate>Sat, 20 Jul 2019 07:19:33 -0400</pubDate>
        </item>
        <item>
        ...
"""

class FeedItem:
    def __init__(self, item, parent_feed):
        self.title = ''
        self.link = ''
        self.guid = ''
        self.guid_permalink = False
        self.description = ''
        self.pub_date = None
        self.parent_feed = parent_feed

        for el in item:
            tag = el.tag.lower()
            if tag == 'title':
                self.title = el.text
            elif tag == 'link':
                self.link = el.text
            elif tag == 'guid':
                self.guid = el.text
                self.guid_permalink = el.attrib.has_key('isPermaLink') and el.attrib.get('isPermaLink') != 'false'
            elif tag == 'description':
                self.description = el.text
            elif tag in ['date', 'pubdate']: # should be 'pubDate' but it's lower()
                try:
                    self.pub_date = parsedate_to_datetime(el.text)
                except:
                    print(_('Error: failed to parse datetime from rfc'))
                if not self.pub_date:
                    try:
                        self.pub_date = datetime.fromisoformat(el.text)
                    except:
                        print(_('Error: failed to parse datetime from iso format'))
            elif tag == 'category':
                # as far as I can tell, the category tag refers to tags for the article
                # at this time I have no need for them.
                pass
            else:
                pass
                #print(_('WARNING: [{0}] unrecognized tag {1}').format(self, el.tag))

    def __repr__(self):
        return f'FeedItem Object `{self.title}` from Feed {self.parent_feed.title}'

    def download_item(self):
        link = self.guid if self.guid_permalink else self.link
        download(link)


class Feed:
    def __init__(self, feedpath):
        with open(feedpath, 'r') as fd:
            tree = etree.parse(fd)
            fd.close()
        root = tree.getroot()
        for elem in root.getiterator():
            if not hasattr(elem.tag, 'find'): continue
            i = elem.tag.find('}')
            if i >=0:
                elem.tag = elem.tag[i+1:]
        objectify.deannotate(root, cleanup_namespaces=True)

        self.confman = ConfManager()
        
        self.title = ''
        self.link = ''
        self.description = ''
        self.language = ''
        self.image_url = ''
        self.items = []

        for el in [*root.xpath('//channel')[0], *root.xpath('//item')]: # root[0] should be channel
            tag = el.tag.lower()
            print(tag)
            if tag == 'title':
                self.title = el.text
            elif tag == 'link' and el.text:
                self.link = el.text
            elif tag == 'description':
                self.description = el.text
            elif tag == 'language':
                self.language = el.text
            elif tag == 'image':
                for iel in el:
                    if iel.tag == 'url':
                        self.image_url = iel.text
                        break
            elif tag == 'item':
                self.items.append(FeedItem(el, self))
            else:
                pass
                # print(_('WARNING: [{0}] unrecognized tag {1}').format(self, el.tag))
        print(self)
        
        self.favicon_path = self.confman.thumbs_cache_path+'/'+shasum(self.link)+'.png'
        if not isfile(self.favicon_path):
            if self.image_url:
                download_raw(self.image_url, self.favicon_path)
            else:
                get_favicon(self.link, self.favicon_path)
        if isfile(self.favicon_path):
            try:
                favicon = Image.open(self.favicon_path)
                if favicon.width > 32:
                    favicon.thumbnail((32, 32), Image.ANTIALIAS)
                    favicon.save(self.favicon_path, 'PNG')
                favicon.close()
            except:
                print(_('Error resizing favicon for feed {0}').format(self.title))


    def __repr__(self):
        return f'Feed Object `{self.title}`; {len(self.items)} items'
