import unittest
from unittest.mock import Mock, MagicMock, patch
from parameterized import parameterized

from gfeeds.rss_parser import FeedItem


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
            # RFC 3339 date, TODO: test with ISO and more, invalid date
            'published': date  # '2020-05-09 10:51:10+03:00'
        }
        feeditem = FeedItem(fp_item, None)
        feeditem.title.should.equal('Test Article')
        feeditem.is_saved.should.equal(False)
        feeditem.link.should.equal('https://planet.gnome.org')
        feeditem.read.should.equal(True)
        # need better way to check datetime
        str(feeditem.pub_date).should.equal('2020-05-09 10:51:10+03:00')
