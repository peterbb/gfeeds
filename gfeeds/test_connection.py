import requests
import threading
from gi.repository import Gtk

def __is_online_async_worker(ret_value_l):
    TEST_URL = 'http://httpbin.org/robots.txt'
    EXPECTED_STATUS = 405
    try:
        res = requests.post(TEST_URL)
        ret_value_l[0] = res.status_code == EXPECTED_STATUS
    except requests.exceptions.ConnectionError:
        ret_value_l[0] = False

def is_online():
    t_ret = [False]
    t = threading.Thread(
        group=None,
        target=__is_online_async_worker,
        name=None,
        args=(t_ret,)
    )
    t.start()
    while t.is_alive():
        while Gtk.events_pending():
            Gtk.main_iteration()
    return t_ret[0]
