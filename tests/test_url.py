import sys

sys.path.insert(0,"../scraper-tools")

from scraper_tools.url import URL, remove_urls, replace_urls
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
                'basename': 'sample',
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
                'basename': 'sample',
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
                'basename': 'sample',
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
                'basename': 'sample',
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
                'basename': 'sample',
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
                'basename': 'sample',
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
                'basename': 'sample',
            }
        },
    ]

class TestClass:
    def test_url_simple_validator(self):
        u = URL()
        assert u.validator('http://example.com') == True
        assert u.validator('ftp://example.com') == True
        assert u.validator('python://example.com') == False
        assert u.validator('python://example.') == False

    def test_url_validator(self):
        for d in test_data:
            url = URL(d['url'])
            assert url.is_valid == d['validate']

    def test_url_parse_attributes(self):
        for d in test_data:
            url = URL(d['url'])
            assert url.attrs == d['attributes']

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

    def test_quote(self):
        expect =  'http://www.sameple.com/%E6%97%A5%E6%9C%AC%E8%AA%9E'
        url = URL('http://www.sameple.com/日本語')
        assert url.url == expect
        assert url.quote('http://www.sameple.com/日本語') == expect

    def test_do_quote(self):
        expect = 'http://www.sameple.com/日本語'
        url = URL('http://www.sameple.com/日本語', do_quote=False)
        assert url.url == expect

    def test_url_quote_safe(self):
        expect = 'http%3A//example.com'
        src_url = 'http://example.com'
        u = URL(safe='/?&@=#%')
        assert u.quote(src_url) == expect

    def test_unquote(self):
        expect =  'http://www.sameple.com/日本語'
        src_url = 'http://www.sameple.com/%E6%97%A5%E6%9C%AC%E8%AA%9E'
        url = URL(src_url)
        assert url.unquote() == expect
        assert url.unquote(src_url) == expect
        assert url.decode() == expect
        assert url.decode(src_url) == expect

    def test_remove_urls(self):
        src_data=(
            "This is sample text.\n"
            "http://www.google.com\n"
            "http://www.yahoo.co.jp\n"
            "[Google](http://www.google.com)\n"
            "[Yahoo Japan](http://www.yahoo.co.jp)\n"
            "Funny HooBar.\n"
        )
        expect=(
            "This is sample text.\n"
            "\n"
            "\n"
            "[Google]()\n"
            "[Yahoo Japan]()\n"
            "Funny HooBar.\n"
        )
        assert remove_urls(src_data) == expect

    def test_remove_urls(self):
        src_data=(
            "This is sample text.\n"
            "https://www.google.com\n"
            "https://www.yahoo.co.jp\n"
            "[Google](https://www.google.com)\n"
            "[Yahoo Japan](https://www.yahoo.co.jp)\n"
            "Funny HooBar.\n"
        )
        expect=(
            "This is sample text.\n"
            "https://www.google.com\n"
            "\n"
            "[Google](https://www.google.com)\n"
            "[Yahoo Japan]()\n"
            "Funny HooBar.\n"
        )
        assert remove_urls(src_data, end_with=".co.jp") == expect

    def test_replace_urls(self):
        src_data=(
            "This is sample text.\n"
            "https://www.google.com\n"
            "https://www.yahoo.co.jp\n"
            "https://example.co.jp/sample?src=csv\n"
            "[Google](https://www.google.com)\n"
            "[Yahoo](https://www.yahoo.co.jp)\n"
            "Funny HooBar.\n"
        )
        expect=(
            "This is sample text.\n"
            "https://www.google.com\n"
            "JAPAN\n"
            "https://example.co.jp/sample?src=csv\n"
            "[Google](https://www.google.com)\n"
            "[Yahoo](JAPAN)\n"
            "Funny HooBar.\n"
        )
        assert replace_urls(src_data,
                            replace="JAPAN",
                            end_with='.co.jp') == expect
