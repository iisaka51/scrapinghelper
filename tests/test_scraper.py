import sys

sys.path.insert(0,"../scrapinghelper")

from scrapinghelper import Scraper
from pprint import pprint
from pathlib import Path

class TestClass:
    def test_get_filename(self):
        s = Scraper()
        url = 'https://github.com/iisaka51/scrapinghelper/blob/main/scrapinghelper/data/20000%20User%20Agents.csv'
        expect = "20000 User Agents.csv"
        assert s.get_filename(url) == expect

    def test_get_filename_with_replace_single(self):
        s = Scraper()
        url = 'https://github.com/iisaka51/scrapinghelper/blob/main/scrapinghelper/data/20000%20User%20Agents.csv'
        expect = "20000_User_Agents.csv"
        assert s.get_filename(url, replace={' ':'_'} ) == expect

    def test_get_filename_with_replace_multi(self):
        s = Scraper()
        url = 'https://github.com/iisaka51/scrapinghelper/blob/main/scrapinghelper/data/20000%20User%20Agents.csv'
        expect = "User_Agents.csv"
        assert s.get_filename(url, replace={' ':'_', '20000_': ''} ) == expect
