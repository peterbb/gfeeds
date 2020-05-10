import unittest
from unittest.mock import Mock, MagicMock, patch, mock_open
from parameterized import parameterized
from datetime import datetime, timezone, timedelta
from .sample_rss import SAMPLE_RSS

from gfeeds.rss_parser import FeedItem, FakeFeed, Feed


class TestFeedItem(unittest.TestCase):

    @parameterized.expand([
        ['2020-05-09 10:51:10+03:00'],  # RFC 3339
        ['2020-05-09T10:51:10+03:00']   # ISO
    ])
    @patch('gfeeds.rss_parser.ConfManager')
    def test_FeedItem_create(self, date, ConfManager_mock):
        confman_mock = ConfManager_mock()
        confman_mock.read_feeds_items = ['https://planet.gnome.org']
        fp_item = {
            'title': 'Test Article',
            'link': 'https://planet.gnome.org',
            'published': date
        }
        feeditem = FeedItem(fp_item, None)
        feeditem.title.should.equal('Test Article')
        feeditem.is_saved.should.be.false
        feeditem.link.should.equal('https://planet.gnome.org')
        feeditem.read.should.be.true
        # need better way to check datetime
        str(feeditem.pub_date).should.equal('2020-05-09 10:51:10+03:00')

    @patch('gfeeds.rss_parser.ConfManager')
    def test_FeedItem_create_malformed_date(self, ConfManager_mock):
        '''
        In case of malformed date, current time should be used
        '''
        confman_mock = ConfManager_mock()
        confman_mock.read_feeds_items = []
        fp_item = {
            'title': 'Test Article',
            'link': 'https://planet.gnome.org',
            'published': 'this is not a date!'
        }
        parent_feed = Mock()
        parent_feed.title = 'Fake feed for testing'
        feeditem = FeedItem(fp_item, parent_feed)
        (
            datetime.now(timezone.utc) - feeditem.pub_date
        ).seconds.should.be.lower_than(1)

    # TODO: test with atom feed, feeds with non utf encodings
    @patch(
            'builtins.open',
            new_callable=mock_open,
            read_data=SAMPLE_RSS.encode()  # wants bytes
    )
    @patch('gfeeds.rss_parser.ConfManager')
    def test_Feed_create(self, ConfManager_mock, mock_file):
        confman_mock = ConfManager_mock()
        download_res = (
            '/some/path',  # feedpath
            'https://planet.gnome.org'  # feed link
        )
        # always have the one article selected, so alter the max article age
        confman_mock.max_article_age = (
            (
                datetime.now(timezone.utc) -
                datetime(2020, 3, 26, 15, 18, tzinfo=timezone.utc)
            ) +
            timedelta(days=100)
        )
        feed = Feed(download_res)

        feed.is_null.should.be.false
        feed.error.should.be.none
        feed.rss_link.should.equal('https://planet.gnome.org')

        # weird, testing a DOC, but feedparser is not a very stable DOC, so
        # testing it on my side has some value
        feed.fp_feed.should.be.a(dict)
        feed.fp_feed.encoding.should.equal('utf-8')
        feed.fp_feed.entries.should.have.length_of(1)

        feed.title.should.equal('Planet GNOME')
        feed.link.should.equal('https://planet.gnome.org/')
        feed.description.should.equal(
            'Planet GNOME - https://planet.gnome.org/'
        )
        feed.items.should.have.length_of(1)
        # TODO: complete this test, there's more
