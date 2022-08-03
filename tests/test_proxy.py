import sys

sys.path.insert(0,"../scrapinghelper")

from scrapinghelper import PROXY, ProxyManager, ProxyRotate
from pprint import pprint
from pathlib import Path

class TestClass:
    def test_proxy_simple_validator(self):
        p = PROXY()
        assert p.validator('http://example.com') == True
        assert p.validator('127.0.0.1:9050') == True
        assert p.validator('socks5://example.com') == True
        assert p.validator('ftp://example.com') == False
        assert p.validator('python://example.com') == False
        assert p.validator('socks://example.com') == False

    def test_proxy_init(self):
        proxy_str = '127.0.0.1:9050'
        expects = {'proxy_url': '127.0.0.1:9050',
                   'is_valid': True,
                   'scheme': 'socks5',
                   'netloc': '127.0.0.1:9050',
                   'username': None,
                   'password': None,
                   'hostname': '127.0.0.1',
                   'port': 9050,
                   'proxy_map': {'http': 'socks5://127.0.0.1:9050',
                    'https': 'socks5://127.0.0.1:9050'}}

        p = PROXY(proxy_str, proxy_type='socks5')
        assert p.proxy_url == proxy_str
        assert p.attrs == expects
        assert p.is_valid == expects['is_valid']
        assert p.scheme == expects['scheme']
        assert p.netloc == expects['netloc']
        assert p.hostname == expects['hostname']
        assert p.port == expects['port']
        assert p.proxy_map == expects['proxy_map']

    def test_proxy_init_with_credential(self):
        proxy_str = 'user:pass@127.0.0.1:9050'
        expects = {'proxy_url': 'user:pass@127.0.0.1:9050',
                   'is_valid': True,
                   'scheme': 'https',
                   'netloc': 'user:pass@127.0.0.1:9050',
                   'username': 'user',
                   'password': 'pass',
                   'hostname': '127.0.0.1',
                   'port': 9050,
                   'proxy_map': {'http': 'https://user:pass@127.0.0.1:9050',
                    'https': 'https://user:pass@127.0.0.1:9050'}}

        p = PROXY(proxy_str)
        assert p.proxy_url == proxy_str
        assert p.attrs == expects
        assert p.is_valid == expects['is_valid']
        assert p.scheme == expects['scheme']
        assert p.netloc == expects['netloc']
        assert p.hostname == expects['hostname']
        assert p.port == expects['port']
        assert p.proxy_map == expects['proxy_map']


    def test_proxy_manager_proxy_as_str(self):
        proxies = 'socks5://127.0.0.1:9050'
        expects = {'proxy_map': {'http': 'socks5://127.0.0.1:9050',
                                 'https': 'socks5://127.0.0.1:9050'} }
        pm = ProxyManager(proxies)
        proxy = pm.random_proxy()
        assert proxy.proxy_map == expects['proxy_map']

    def test_proxy_manager_single_proxy(self):
        proxies = ['socks5://127.0.0.1:9050']
        expects = {'proxy_map': {'http': 'socks5://127.0.0.1:9050',
                                 'https': 'socks5://127.0.0.1:9050'} }
        pm = ProxyManager(proxies)
        proxy = pm.random_proxy()
        assert proxy.proxy_map == expects['proxy_map']

    def test_proxy_manager_multiple_proxy(self):
        proxies = ['socks5://127.0.0.1:9050', 'socks5://127.0.0.1:9070']
        expects = {'proxy_map': [
                       {'http': 'socks5://127.0.0.1:9050',
                       'https': 'socks5://127.0.0.1:9050'},
                       {'http': 'socks5://127.0.0.1:9070',
                       'https': 'socks5://127.0.0.1:9070'},
                       ] }
        pm = ProxyManager(proxies)
        proxy = pm.next_proxy()
        assert proxy.proxy_map == expects['proxy_map'][0]
        proxy = pm.next_proxy()
        assert proxy.proxy_map == expects['proxy_map'][1]
        proxy = pm.get_proxy()  # default is ProxyRotate.NEXT
        assert proxy.proxy_map == expects['proxy_map'][0]
        proxy = pm.get_proxy(ProxyRotate.NEXT)
        assert proxy.proxy_map == expects['proxy_map'][1]
        proxy = pm.get_proxy(ProxyRotate.KEEP)
        assert proxy.proxy_map == expects['proxy_map'][1]

    def test_proxy_manager_from_file(self):
        this_directory = Path(__file__).parent
        datapath = 'file://{}/proxy_test.csv'.format(this_directory)
        expects = {'proxy_map': {'http': 'socks5://127.0.0.1:9050',
                                 'https': 'socks5://127.0.0.1:9050'} }
        pm = ProxyManager(proxies=datapath)
        proxy = pm.random_proxy()
        assert proxy.proxy_map == expects['proxy_map']

    def test_proxy_manager_loadproxies(self):
        this_directory = Path(__file__).parent
        datapath = 'file://{}/proxy_test.csv'.format(this_directory)
        expects = {'proxy_map': {'http': 'socks5://127.0.0.1:9050',
                                 'https': 'socks5://127.0.0.1:9050'} }
        pm = ProxyManager()
        pm.load_proxies(datapath)
        proxy = pm.random_proxy()
        assert proxy.proxy_map == expects['proxy_map']

