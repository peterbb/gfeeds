import unittest
from unittest.mock import Mock, MagicMock, patch
from parameterized import parameterized
from datetime import datetime, timezone

from gfeeds.rss_parser import FeedItem, FakeFeed


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

    # @patch('gfeeds.rss_parser.ConfManager')
    # def test_Feed_create(self, ConfManager_mock):
    #     pass
