from gettext import gettext as _
import requests
from .confManager import ConfManager
from .sha import shasum
from os.path import isfile
# import brotli

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
            fd.close()
        return toret
    res = requests.get(link, headers=GET_HEADERS)
    if 200 <= res.status_code <= 299:
        return res.text
    else:
        print(f'requreq.textest code {res.status_code}')
        raise requests.HTTPError(f'requreq.textest code {res.status_code}')

def download_raw(link, dest):
    res = requests.get(link, headers=GET_HEADERS)
    if res.status_code == 200:
        with open(dest, 'wb') as fd:
            for chunk in res.iter_content(1024):
                fd.write(chunk)
            fd.close()
    else:
        raise requests.HTTPError(f'request code {res.status_code}')

def download_feed(link, get_cached=False):
    dest_path = confman.cache_path.joinpath(shasum(link)+'.rss')
    if get_cached:
        if isfile(dest_path):
            return (dest_path, link)
        else:
            return ('not_cached', None)
    # print(_('Downloading `{0}`…').format(link))
    headers = GET_HEADERS.copy()
    if 'last-modified' in confman.conf['feeds'][link].keys() and isfile(dest_path):
        headers['If-Modified-Since'] = confman.conf['feeds'][link]['last-modified']
    try:
        res = requests.get(link, headers=headers)
    except:
        return (False, _('`{0}` is not an URL').format(link))
    if 'last-modified' in res.headers.keys():
        confman.conf['feeds'][link]['last-modified'] = res.headers['last-modified']
    if res.status_code == 200:
        text = res.text
        if not 'last-modified' in res.headers.keys():
            if 'last-modified' in confman.conf['feeds'][link].keys():
                confman.conf['feeds'][link].pop('last-modified')
        # if 'content-encoding' in res.headers.keys():
        #     if res.headers['content-encoding'] == 'br':
        #         text = brotli.decompress(res.content).decode()
        with open(dest_path, 'w') as fd:
            fd.write(text)
            fd.close()
        return (dest_path, link)
    elif res.status_code == 304:
        return (dest_path, link)
    else:
        error_txt = _('Error downloading `{0}`, code `{1}`').format(link, res.status_code)
        print(error_txt)
        return (False, error_txt)
