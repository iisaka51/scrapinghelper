import random
from itertools import cycle
from typing import Optional
import pandas as pd
from .url import URL

PUBLIC_PROXIES = {
    "TheSpeedX": (
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/"
        "master/socks5.txt" ),
    "Hookzof" : (
        "https://raw.githubusercontent.com/hookzof/"
        "socks5_list/master/proxy.txt" ),
}

class PROXY(object):
    def __init__(self,
        proxy_config: Optional[str]=None
        ):
        self.proxy_config = URL(proxy_config)
        ip_port = self.proxy_config.netloc.split(':')
        self.ip = ip_port[0]
        self.port = ip_port[1] if len(ip_port)>1 else ''
        self.username = self.proxy_config.username
        self.password = self.proxy_config.password

    def to_dict(self):
        if self.proxy_config:
            proxy_dict = {
                'http': self.proxy_config,
                'https': self.proxy_config
            }
        else:
            proxy_dict = {}
        return proxy_dict

class ProxyManager(object):
    def __init__(self, source='TheSpeedX'):
        self.proxies = self.load_proxies(source)
        self.proxies_pool = cycle(self.proxies)

    @staticmethod
    def show_proxies_source():
        return [x for x in PUBLIC_PROXIES.keys()]

    def load_proxies(self, source='TheSpeedX'):
        if source in PUBLIC_PROXIES:
            url = PUBLIC_PROXIES[source]
            df = pd.read_csv(url, names=['proxy'])
            df['proxy'] = 'socks5://' + df['proxy'].astype(str)
            pool =  [ PROXY(x).to_dict()
                      for x in df['proxy'].values.tolist()]
            return pool

    def get_random_proxy(self):
        return random.choice(self.proxies)

    def next_proxy(self):
        return next(self.proxies_pool)
