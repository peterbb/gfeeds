from gettext import gettext as _
import listparser
from os.path import isfile

def opml_to_rss_list(opml_path):
    if not isfile(opml_path):
        print(_('Error: OPML path provided does not exist'))
        return []
    try:
        lp_opml = listparser.parse(opml_path)
        n_feeds_urls_l = [f['url'] for f in lp_opml['feeds']]
        return n_feeds_urls_l
    except:
        print(_('Error parsing OPML file `{0}`').format(opml_path))
        return []
