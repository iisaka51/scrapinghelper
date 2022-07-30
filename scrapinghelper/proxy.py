import re
import random
from urllib.parse import urlparse
from pathlib import Path
from itertools import cycle
from typing import Optional, NamedTuple
import pandas as pd

PUBLIC_PROXIES = {
    "TheSpeedX": (
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/"
        "master/socks5.txt" ),
    "Hookzof" : (
        "https://raw.githubusercontent.com/hookzof/"
        "socks5_list/master/proxy.txt" ),
}

IP_MIDDLE_OCTET = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
IP_LAST_OCTET = r"(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))"

PROXY_PATTERN = ( # noqa: W605
    # protocol identifier
    r"((?P<scheme>https?|socks[45]|direct|quick)://)?"
    # user:pass authentication
    r"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    r"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    r"(?:"
    r"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    r"(?:(?:10|127)" + IP_MIDDLE_OCTET + r"{2}" + IP_LAST_OCTET + r")|"
    r"(?:(?:169\.254|192\.168)" + IP_MIDDLE_OCTET + IP_LAST_OCTET + r")|"
    r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + IP_MIDDLE_OCTET + IP_LAST_OCTET + r"))"
    r"|"
    # private & local hosts
    r"(?P<private_host>"
    r"(?:localhost))"
    r"|"
    # IP address dotted notation octets
    r"(?P<public_ip>"
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"" + IP_MIDDLE_OCTET + r"{2}"
    r"" + IP_LAST_OCTET + r")"
    # host name
    r"(?:(?:(?:xn--[-]{0,2})|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)"
    # domain name
    r"(?:\.(?:(?:xn--[-]{0,2})|[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]-?)*"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]+)*"
    # TLD identifier
    r"(?:\.(?:(?:xn--[-]{0,2}[a-z\u00a1-\uffff\U00010000-\U0010ffff0-9]{2,})|"
    r"[a-z\u00a1-\uffff\U00010000-\U0010ffff]{2,}))"
    r")"
    # port number
    r"(?::\d{2,5})?"
)

re_pattern = re.compile( r"^" + PROXY_PATTERN + r"$", re.UNICODE | re.IGNORECASE)

class ProxyParseError(BaseException):
    pass

class ResultProxyValidator(NamedTuple):
    proxy_url: str
    is_valid: bool
    scheme: str
    netloc: str
    username: Optional[str]
    password: Optional[str]
    hostname: str
    port: Optional[str]
    as_dict: dict

def proxyparse(
        value: str,
        proxy_type='https'
    ) -> ResultProxyValidator:
    """
    Parameters
    ----------
    value: str
        PROXY string to validate
    proxy_type: str
        PROXY type. default is 'https'
    Returns
    -------
    result: ResulttProxyValidator
    """

    if value and not isinstance(value, str):
        value = str(value)

    check = re_pattern.match(value)
    if not check:
        raise ProxyParseError('Invalid proxy string')

    c = any(value.startswith(x) for x in ['http', 'socks', 'direct', 'quiC'])
    if not c:
         url_prefix = f'{proxy_type}://' if proxy_type else ''
         proxy_str = f'{url_prefix}{value}'
    else:
         url_prefix = ''

    proxy_url =  value
    is_valid = True
    v = urlparse(proxy_str)
    scheme = v.scheme
    netloc = v.netloc
    username = v.username
    password = v.password
    hostname = v.hostname
    port = v.port
    as_dict =  {'http': f'{url_prefix}{str(proxy_url)}',
                'https': f'{url_prefix}{str(proxy_url)}' }

    return ResultProxyValidator( proxy_url, is_valid,
                        scheme, netloc, username, password,
                        hostname, port, as_dict )

def proxy_validator(value, public=False):
    """
    Return whether or not givven value is a valid PROXY.
    If the value is valid PROXY this function returns ``True``,
    otherwise ``False```.

    This validator is based on `validator of dperini`
    See Also: https://gist.github.com/dperini/729294

    Examples::

        >>> proxy_validator('http://example.com')
        True

        >>> proxy_validator('socks5://127.0.0.1:9050')
        True

        >>> proxy_validator('ftp://example.com')
        False

        >>> proxy_validator('http://example.d')
        False

        >>> proxy_validator('http://10.0.0.1')
        True

        >>> proxy_validator('http://10.0.0.1', public=True)
        False

    Parameters
    ----------
    value: str
        PROXY string to validate
    public: bool
         If set True to only allow a public IPAddress. (default is False)

    Returns
    -------
    result: bool
        Return ``True`` if the value is valid URL, otherwise ``False``
    """

    check = re_pattern.match(value)
    if public:
        result = check and not any( check.groupdict().get(key)
                                    for key in ('private_ip', 'private_host'))
    else:
        result = check

    result = True if result else False
    return result

class PROXY(object):
    def __init__(self,
        proxy_str: Optional[str]=None,
        proxy_type: str='https',
        ) -> ResultProxyValidator:
        self.validate = self.__validator(proxy_str, proxy_type)
        self.__dict__.update(self.validate.as_dict)

    def validator(self, proxy_str: str) -> bool:
        """
        Return whether or not given value is a valid URL
        If the value is valid URL this function returns ``True``,
        otherwise ``False``.

        Parameters
        ----------
        proxy_str: str
            The input proxy_str

        Examples
        --------
        >>> from scrapinghelper import PROXY
        >>> p = PROXY()
        >>> p.validator('127.0.0.1:9050')
        True

        >>> p.validator('ftp://example.com')
        False

        >>> p('http://10.0.0.1')
        True

        """
        return self.__validator(url).is_valid

    def __validator(self,
        proxy_str: str,
        proxy_type: str='https',
    ) -> ResultProxyValidator:

        try:
            v = proxyparse(proxy_str, proxy_type)
            _is_valid =  v.is_valid
            _scheme = v.scheme
            _netloc = v.netloc
            _username = v.username
            _password = v.password
            _hostname =  v.hostname
            _port = v.port
            _as_dict = v.as_dict
        except:
            _is_valid = False
            _scheme = ''
            _netloc = ''
            _username = None
            _password = None
            _hostname =  ''
            _port = None
            _as_dict = {}

        result = ResultProxyValidator(
                    proxy_str, _is_valid,
                    _scheme, _netloc,
                    _username, _password, _hostname, _port, _as_dict )

        return result

    @property
    def attrs(self):
        return self.validate._asdict()

    def __repr__(self) -> str:
        return str(self.proxy_str)


class ProxyManager(object):
    def __init__(self, proxies_url=None):
        self.proxies_url = ( self.normalized_proxies_url(proxies_url)
                             or PUBLIC_PROXIES['Hookzof'] )
        self.proxies = self.load_proxies(self.proxies_url)
        self.proxies_pool = cycle(self.proxies)

    @staticmethod
    def show_proxies_source():
        return [x for x in PUBLIC_PROXIES.keys()]

    def normalized_proxies_url(self, proxies_url):
        if  proxies_url:
            return None

        proxies_url = str(proxies_url)
        if proxies_url.startswith('file://.'):
            proxies_url = proxies_url.replace('file://.','')
            this_directory = Path(__file__).parent
            proxies_url = f'file://{str(this_directory / proxies_url )}'
        return proxies_url

    def load_proxies(self, proxies_url=None, proxy_type='socks5'):
        df = pd.read_csv(self.proxies_url, names=['proxy'])
        df['proxy'] = f'{proxy_type}://' + df['proxy'].astype(str)
        pool =  [ PROXY(x).to_dict()
                  for x in df['proxy'].values.tolist()]
        return pool

    def random_proxy(self):
        return random.choice(self.proxies)

    def next_proxy(self):
        return next(self.proxies_pool)
