from lxml.html import html5parser
import requests
from .download_manager import download_raw
from gettext import gettext as _
from urllib.parse import urlparse

def get_favicon(link, favicon_path):
    req = requests.get(link)
    if req.status_code != 200:
        return None
    html = req.text
    root = html5parser.fromstring(html if type(html) == str else html.decode())
    favicon_els = root.xpath(
        '//x:link',
        namespaces={'x': 'http://www.w3.org/1999/xhtml'}
    )
    candidate = {
        'path': '',
        'is_absolute': False,
        'size': -1
    }
    for e in favicon_els:
        if candidate['size'] >= 32:
            break
        if 'rel' in e.attrib.keys():
            size = 0
            can_save = False
            if e.attrib['rel'] == 'apple-touch-icon':
                size = 1
                can_save = True
                if 'sizes' in e.attrib.keys():
                    size = int(e.attrib['sizes'].split('x')[0])
            elif e.attrib['rel'] in ['icon', 'shortcut icon'] and candidate['size'] == -1:
                size = 0
                can_save = True
            if can_save:
                candidate['path'] = e.attrib['href']
                candidate['is_absolute'] = 'http://' in e.attrib['href'] or 'https://' in e.attrib['href']
                candidate['size'] = size
    p = candidate['path']
    if not p:
        return None
    if not candidate['is_absolute']:
        if p[0:2] == '//':
            p = p[2:]
        elif p[0] == '/':
            p = p[1:]
        up = urlparse(link)
        url = f'{up.scheme or "http"}://{up.hostname}/{p}'
        try:
            download_raw(url, favicon_path)
        except:
            try:
                url = f'{up.scheme or "http"}://{p}'
                download_raw(url, favicon_path)
            except:
                print(_('Error downloading favicon for `{0}`').format(link))
    else:
        download_raw(p, favicon_path)
