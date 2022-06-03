import sys

sys.path.insert(0,"../web_scrapper")

from web_scrapper import URL, Scrapper, LogConfig

class TestClass:
    test_url = 'https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unicode'
    expect_result = { 'url': test_url,
               'is_valid': True,
               'scheme': 'https',
               'netloc': 'www.houjin-bangou.nta.go.jp',
               'path': '/download/zenken/',
               'params': '',
               'query': '',
               'fragment': 'csv-unicode',
             }

    def test_url_dict(self):
        url = URL(self.test_url)
        assert url.__dict__ == expect_result

    def test_url_validator(self):
        url = URL(self.test_url)
        assert url.validator(self.test_url) == True

