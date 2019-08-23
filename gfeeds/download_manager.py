from gettext import gettext as _
import requests
from .confManager import ConfManager
from .sha import shasum

confman = ConfManager()

def download_text(link):
    res = requests.get(link)
    if res.status_code == 200:
        return res.text
    else:
        raise requests.HTTPError(f'request code {res.status_code}')

def download_raw(link, dest):
    res = requests.get(link)
    if res.status_code == 200:
        with open(dest, 'wb') as fd:
            for chunk in res.iter_content(1024):
                fd.write(chunk)
            fd.close()
    else:
        raise requests.HTTPError(f'request code {res.status_code}')

def download_feed(link):
    dest_path = confman.cache_path.joinpath(shasum(link)+'.rss')
    #print(_('Downloading `{0}`…').format(link))
    headers = {
        'Accept-Encoding': 'gzip, deflate, br'
    }
    if 'last-modified' in confman.conf['feeds'][link].keys():
        headers['If-Modified-Since'] = confman.conf['feeds'][link]['last-modified']
    res = requests.get(link, headers = headers)
    if 'last-modified' in res.headers.keys():
        confman.conf['feeds'][link]['last-modified'] = res.headers['last-modified']
    if res.status_code == 200:
        #print(_('Download of `{0}` successful').format(link))
        with open(dest_path, 'w') as fd:
            fd.write(res.text)
            fd.close()
        return (dest_path, link)
    elif res.status_code == 304:
        return (dest_path, link)
    else:
        print(_('Error downloading `{0}`, code `{1}`').format(link, res.status_code))
        return None
