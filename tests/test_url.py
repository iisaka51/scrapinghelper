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
