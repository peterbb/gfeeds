from urllib.parse import urlparse


def __build_url(scheme='http', netloc='', path=''):
    return urlparse(
        (scheme + '://') +
        netloc +
        path
    )


def sanitize(base, url):
    parsed_base = urlparse(base)
    parsed_url = urlparse(url)
    if not parsed_url.scheme:
        parsed_url = __build_url(
            parsed_base.scheme,
            parsed_url.netloc,
            parsed_url.path
        )
    if not parsed_url.netloc:
        parsed_url = __build_url(
            parsed_url.scheme,
            parsed_base.netloc,
            parsed_url.path
        )
    return parsed_url.geturl()
