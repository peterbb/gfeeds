from lxml.html import html5parser
import requests
from .download_manager import download_raw

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
    if not candidate['is_absolute']:
        p = link +'/'+ p
    print(p)
    download_raw(p, favicon_path)
