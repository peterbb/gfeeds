from gettext import gettext as _
import requests
from .confManager import ConfManager
from .sha import shasum

confman = ConfManager()

def download_text(link):
    req = requests.get(link)
    if req.status_code == 200:
        return req.text
    else:
        raise requests.HTTPError(f'request code {req.status_code}')

def download_raw(link, dest):
    req = requests.get(link)
    if req.status_code == 200:
        with open(dest, 'wb') as fd:
            for chunk in req.iter_content(1024):
                fd.write(chunk)
            fd.close()
    else:
        raise requests.HTTPError(f'request code {req.status_code}')

def download_feed(link):
    dest_path = confman.cache_path.joinpath(shasum(link)+'.rss')
    #print(_('Downloading `{0}`…').format(link))
    req = requests.get(link)
    if req.status_code == 200:
        #print(_('Download of `{0}` successful').format(link))
        needs_save = False
        if dest_path.is_file():
            with open(dest_path, 'r') as fd:
                if shasum(req.text) == shasum(fd.read()):
                    pass
                    #print(_('Hit cache for `{0}`, skipping file update').format(link))
                else:
                    needs_save = True
                fd.close()
        else:
            needs_save = True
        if needs_save:
            with open(dest_path, 'w') as fd:
                fd.write(req.text)
                fd.close()
        return (dest_path, link)
    else:
        print(_('Error downloading `{0}`, code `{1}`').format(link, req.status_code))
        return None
