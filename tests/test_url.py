import sys

sys.path.insert(0,"../scrapper-tools")

from scrapper_tools.url import URL
from pprint import pprint

test_data = [
        {
            'url': 'https://www.example.com/download/#csv-unicode',
            'validate': True,
            'attributes': {
                'url': 'https://www.example.com/download/#csv-unicode',
                'is_valid': True,
                'scheme': 'https',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'path': '/download/',
                'params': '',
                'query': '',
                'fragment': 'csv-unicode',
             }
        },
        {
            'url': 'http://user:password@www.example.com:8080/sample',
            'validate': True,
            'attributes': {
                'url': 'http://user:password@www.example.com:8080/sample',
                'is_valid': True,
                'scheme': 'http',
                'netloc': 'user:password@www.example.com:8080',
                'hostname': 'www.example.com',
                'port': 8080,
                'username': 'user',
                'password': 'password',
                'path': '/sample',
                'params': '',
                'query': '',
                'fragment': '',
            }
        },
        {
            'url': 'http://www.example.com/sample?src=git&encode=jp',
            'validate': True,
            'attributes': {
                'url': 'http://www.example.com/sample?src=git&encode=jp',
                'is_valid': True,
                'scheme': 'http',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'path': '/sample',
                'params': '',
                'query': 'src=git&encode=jp',
                'fragment': '',
            }
        },
        {
            'url': 'http://www.example.com/space%20here.html',
            'validate': True,
            'attributes': {
                'url': 'http://www.example.com/space%20here.html',
                'is_valid': True,
                'scheme': 'http',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'path': '/space%20here.html',
                'params': '',
                'query': '',
                'fragment': '',
            }
        },
        {
            'url': 'http://www.example.com/and%26here.html',
            'validate': True,
            'attributes': {
                'url': 'http://www.example.com/and%26here.html',
                'is_valid': True,
                'scheme': 'http',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'path': '/and%26here.html',
                'params': '',
                'query': '',
                'fragment': '',
            }
        },
        {
            'url': 'http://www.example.com/and&here.html',
            'validate': True,
            'attributes': {
                'url': 'http://www.example.com/and&here.html',
                'is_valid': True,
                'scheme': 'http',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'path': '/and&here.html',
                'params': '',
                'query': '',
                'fragment': '',
            }
        },
        {
            'url': 'htttp://www.example.com',
            'validate': False,
            'attributes': {
                'url': 'htttp://www.example.com',
                'is_valid': False,
                'scheme': 'htttp',
                'netloc': 'www.example.com',
                'hostname': 'www.example.com',
                'port': None,
                'username': None,
                'password': None,
                'path': '',
                'params': '',
                'query': '',
                'fragment': '',
            }
        },
    ]

class TestClass:
    def test_url_validator(self):
        for d in test_data:
            url = URL(d['url'])
            assert url.is_valid == d['validate']

    def test_url_parse_attributes(self):
        for d in test_data:
            url = URL(d['url'])
            assert url.__dict__ == d['attributes']

    def test_url_get_query_val(self):
        url = URL('http://www.example.com/sample?src=git&encode=jp')
        assert url.get_query_val('src') == 'git'
        assert url.get_query_val('encode') == 'jp'

    def test_url_set_query_val(self):
        expect1 = 'http://www.example.com/sample?src=csv&encode=jp'
        expect2 = 'http://www.example.com/sample?src=git&encode=en'
        url = URL('http://www.example.com/sample?src=git&encode=jp')
        assert url.set_query_val('src', 'csv') == expect1
        assert url.set_query_val('encode', 'en') == expect2

    def test_strip_query(self):
        expect = 'http://www.example.com/sample'
        url = URL('http://www.example.com/sample?src=git&encode=jp')
        assert url.strip_query() == expect

    def test_get_root_address(self):
        expect = 'http://www.example.com'
        url = URL('http://www.example.com/sample?src=git&encode=jp')
        assert url.get_root_address() == expect

    def test_encode(self):
        expect =  'http://www.sameple.com/%E6%97%A5%E6%9C%AC%E8%AA%9E'
        url = URL('http://www.sameple.com/日本語')
        assert url.url == expect
        assert url.encode('http://www.sameple.com/日本語') == expect

    def test_decode(self):
        expect =  'http://www.sameple.com/日本語'
        url = URL('http://www.sameple.com/%E6%97%A5%E6%9C%AC%E8%AA%9E')
        assert url.decode() == expect
        assert url.decode('http://www.sameple.com/%E6%97%A5%E6%9C%AC%E8%AA%9E') == expect
