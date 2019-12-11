from gettext import gettext as _
import requests
from .confManager import ConfManager
from .sha import shasum
from os.path import isfile
from lxml.html import html5parser
from .url_sanitizer import sanitize

confman = ConfManager()

GET_HEADERS = {
    'User-Agent': 'gfeeds/1.0',
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate'
}

# will return the content of a file if it's a file url
def download_text(link):
    if link[:8] == 'file:///':
        with open(link[7:]) as fd:
            toret = fd.read()
        return toret
    res = requests.get(link, headers=GET_HEADERS)
    if 200 <= res.status_code <= 299:
        return res.text
    else:
        print(f'response code {res.status_code}')
        raise requests.HTTPError(f'response code {res.status_code}')

def download_raw(link, dest):
    res = requests.get(link, headers=GET_HEADERS)
    if res.status_code == 200:
        with open(dest, 'wb') as fd:
            for chunk in res.iter_content(1024):
                fd.write(chunk)
    else:
        raise requests.HTTPError(f'response code {res.status_code}')

def extract_feed_url_from_html(link):
    html = download_text(link)
    root = html5parser.fromstring(html if type(html) == str else html.decode())
    link_els = root.xpath(
        '//x:link',
        namespaces={'x': 'http://www.w3.org/1999/xhtml'}
    )
    for el in link_els:
        if (
            el.attrib.get('rel', '') == 'alternate' and
            el.attrib.get('type', '') in (
                'application/atom+xml', 'application/rss+xml'
            ) and 'href' in el.attrib.keys()
        ):
            return sanitize(link, el.attrib['href'])
    return None

def download_feed(link, get_cached=False):
    dest_path = confman.cache_path.joinpath(shasum(link)+'.rss')
    if get_cached:
        return (dest_path, link) if isfile(dest_path) else ('not_cached', None)
    headers = GET_HEADERS.copy()
    if (
            'last-modified' in confman.conf['feeds'][link].keys() and
            isfile(dest_path)
    ):
        headers['If-Modified-Since'] = confman.conf['feeds'][link]['last-modified']
    try:
        res = requests.get(
            link, headers=headers, allow_redirects=False
        )
    except:
        return (False, _('`{0}` is not an URL').format(link))
    if 'last-modified' in res.headers.keys():
        confman.conf['feeds'][link]['last-modified'] = res.headers['last-modified']

    def handle_200():
        if (
                not 'last-modified' in res.headers.keys() and
                'last-modified' in confman.conf['feeds'][link].keys()
        ) :
            confman.conf['feeds'][link].pop('last-modified')
        with open(dest_path, 'w') as fd:
            fd.write(res.text)
        return (dest_path, link)

    handle_304 = lambda: (dest_path, link)

    def handle_301_302():
        n_link = res.headers.get('location', link)
        confman.conf['feeds'][n_link] = confman.conf['feeds'][link]
        confman.conf['feeds'].pop(link)
        return download_feed(n_link)

    handle_everything_else = lambda: (
        False,
        _('Error downloading `{0}`, code `{1}`').format(link, res.status_code)
    )

    handlers = {
        200: handle_200, 304: handle_304,
        301: handle_301_302, 302: handle_301_302
    }
    return handlers.get(res.status_code, handle_everything_else)()
