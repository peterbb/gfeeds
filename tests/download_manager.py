import unittest
import httpretty
import sure
from os import remove
from os.path import isfile

from .sample_html import SAMPLE_HTML, RSS_URL, ATOM_URL

import gi
gi.require_version('Gtk', '3.0')

from gfeeds.download_manager import (
    download_text,
    download_raw,
    extract_feed_url_from_html
)


class TestDownloadManager(unittest.TestCase):

    @httpretty.activate
    def test_download_text(self):
        url = 'https://gfeeds.gabmus.org/text'
        httpretty.register_uri(
            httpretty.GET,
            url,
            body='This is just some text'
        )

        download_text(url).should.equal('This is just some text')

    @httpretty.activate
    def test_download_raw(self):
        url = 'https://gfeeds.gabmus.org/raw'
        httpretty.register_uri(
            httpretty.GET,
            url,
            body='This is just some text'
        )

        dest = '/tmp/org.gabmus.gfeeds_test_download_raw.txt'
        if isfile(dest):
            remove(dest)
        download_raw(url, dest)
        isfile(dest).should.equal(True)
        with open(dest, 'r') as fd:
            fd.read().should.equal('This is just some text')
        remove(dest)

    @httpretty.activate
    def test_extract_feed_url_from_html(self):
        url = 'https://planet.gnome.org'
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=SAMPLE_HTML
        )
        (RSS_URL, ATOM_URL).should.contain(extract_feed_url_from_html(url))
