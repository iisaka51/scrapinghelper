import sys

sys.path.insert(0,"../scrapinghelper")

from scrapinghelper import PROXY
from pprint import pprint

test_data = [
        {
            'proxy_str': 'https://www.example.com:8080',
            'validate': True,
            'attributes': {
                'proxy_str': 'https://www.example.com:8080',
                'is_valid': True,
                'scheme': 'https',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'as_dit': { 'http': 'https://www.example.com:8080',
                            'https': 'https://www.example.com:8080' }
             }
        },
    ]

class TestClass:
    def test_url_simple_validator(self):
        u = PROXY()
        assert u.validator('http://example.com') == True
        assert u.validator('127.0.0.1:9050') == True
        assert u.validator('socks5://example.com') == True
        assert u.validator('ftp://example.com') == False
        assert u.validator('python://example.com') == False
        assert u.validator('socks://example.com') == False
