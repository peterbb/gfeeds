import requests

def is_online():
    TEST_URL = 'http://httpbin.org/robots.txt'
    EXPECTED_STATUS = 405
    try:
        res = requests.post(TEST_URL)
        return res.status_code == EXPECTED_STATUS
    except requests.exceptions.ConnectionError:
        return False
