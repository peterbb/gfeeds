import unittest
from unittest.mock import Mock, MagicMock, patch
import httpretty
import sure
from os import remove, makedirs, rmdir
from os.path import isfile
from gfeeds.download_manager import (
    download_text,
    download_raw,
    extract_feed_url_from_html,
    download_feed
)
from .sample_html import SAMPLE_HTML, RSS_URL, ATOM_URL
from .sample_rss import SAMPLE_RSS


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

    # TODO: tests for most http return codes
    @patch('gfeeds.download_manager.confman')
    @httpretty.activate
    def test_download_feed(self, mock_confman):
        url = 'https://planet.gnome.org/rss20.xml'
        httpretty.register_uri(
            httpretty.GET,
            url,
            body=SAMPLE_RSS
        )
        cache_path = '/tmp'
        feed_filename = 'org.gabmus.gfeeds_test_mock_feed_path_sha'
        feed_destpath = f'{cache_path}/{feed_filename}'
        mock_confman.conf = {'feeds': {url: {}}}
        mock_confman.cache_path = Mock()
        mock_confman.cache_path.__repr__ = MagicMock(return_value=cache_path)
        mock_confman.cache_path.joinpath = MagicMock(
            return_value=feed_destpath
        )
        ret = download_feed(url)
        ret[0].should.equal(feed_destpath)
        ret[1].should.equal(url)

        with open(feed_destpath) as fd:
            fd.read().should.equal(SAMPLE_RSS)
        if isfile(feed_destpath):
            remove(feed_destpath)

    @patch('gfeeds.download_manager.confman')
    @patch('gfeeds.download_manager._', side_effect=lambda s: s)
    @httpretty.activate
    def test_download_feed_404(self, mock_confman, mock_gettext):
        url = 'https://planet.gnome.org/notfound'
        httpretty.register_uri(
            httpretty.GET,
            url,
            status=404
        )
        cache_path = '/tmp'
        feed_filename = 'org.gabmus.gfeeds_test_mock_feed_path_sha'
        feed_destpath = f'{cache_path}/{feed_filename}'
        mock_confman.conf = {'feeds': {url: {}}}
        mock_confman.cache_path = Mock()
        mock_confman.cache_path.__repr__ = MagicMock(return_value=cache_path)
        mock_confman.cache_path.joinpath = MagicMock(
            return_value=feed_destpath
        )
        ret = download_feed(url)
        ret[0].should.equal(False)
        ret[1].should.equal(f'Error downloading `{url}`, code `404`')
        isfile(feed_destpath).should.equal(False)
        if isfile(feed_destpath):
            remove(feed_destpath)
