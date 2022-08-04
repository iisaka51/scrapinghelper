import os
import re
import random
import itertools
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional, Union, NamedTuple
from enum import Enum
import pandas as pd

IP_MIDDLE_OCTET = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
IP_LAST_OCTET = r"(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))"

PROXY_PATTERN = ( # noqa: W605
    # protocol identifier
    r"(?:(?:(?P<scheme>https?|socks[45]|direct|quick))://)?"
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
    r"|"
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

class ProxyRotate( Enum):
    NO_PROXY = 1
    KEEP = 2
    NEXT = 3
    RANDOM = 4

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
    proxy_map: dict

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

    c = any(value.startswith(x) for x in ['http', 'socks', 'direct', 'quic'])
    if not c:
         url_prefix = '{}://'.format(proxy_type) if proxy_type else ''
         proxy_str = '{}{}'.format(url_prefix,value)
    else:
         url_prefix = ''
         proxy_str = value

    proxy_url =  value
    is_valid = True
    v = urlparse(proxy_str)
    scheme = v.scheme
    netloc = v.netloc
    username = v.username
    password = v.password
    hostname = v.hostname
    port = v.port
    proxy_map =  {'http': '{}{}'.format(url_prefix, str(proxy_url)),
                  'https': '{}{}'.format(url_prefix, str(proxy_url)) }

    return ResultProxyValidator( proxy_url, is_valid,
                        scheme, netloc, username, password,
                        hostname, port, proxy_map )

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
        self.proxy_url: str
        self.is_valid: bool
        self.scheme: str
        self.netloc: str
        self.username: Optional[str]
        self.password: Optional[str]
        self.hostname: str
        self.port: Optional[str]
        self.proxy_map: dict

        self.validate = self.__validator(proxy_str, proxy_type)
        self.__dict__.update(self.validate._asdict())

    def validator(self, proxy_str: str) -> bool:
        """Validator for PROXY strings.

        Parameters
        ----------
        proxy_str: str
            The input string of proxy.

        Returns
        -------
        Return whether or not given value is a valid PROXY.
        If the proxy_str is valid PROXY this function returns
        ``True``, otherwise ``False``.

        Examples
        --------
        >>> from scrapinghelper import PROXY
        >>> p = PROXY()
        >>> p.validator('127.0.0.1:9050')
        True

        >>> p.validator('ftp://example.com')
        False

        >>> p.validator('http://10.0.0.1')
        True

        >>> p.load_proxies('file:///tmp/myproxies.csv')

        >>> p.load_proxies('https://somewhere.com/share/myproxies.csv')

        >>> p = PROXY('file:///tmp/myproxies.csv')

        >>> p = PROXY('https://somewhere.com/share/myproxies.csv')

        >>> p = PROXY(['127.0.0.1:9050'])

        """
        return self.__validator(proxy_str).is_valid

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
            _proxy_map = v.proxy_map
        except:
            _is_valid = False
            _scheme = ''
            _netloc = ''
            _username = None
            _password = None
            _hostname =  ''
            _port = None
            _proxy_map = {}

        result = ResultProxyValidator(
                    proxy_str, _is_valid,
                    _scheme, _netloc,
                    _username, _password,
                    _hostname, _port, _proxy_map )

        return result

    @property
    def attrs(self):
        return self.validate._asdict()

    def __repr__(self) -> str:
        return str(self.validate.proxy_url)


class ProxyManager(object):
    def __init__(self, proxies: Optional[Union[list,str]]=None):
        """ Proxy Manager
        load proxy data and create proxy pool
        Parameters
        ----------
        proxies: proxies: Optional[Union[list,str]]=None
            list of proxies
            if proxies startswith 'file://', load proxies from file.
            if proxies startswith 'https://', load proxies from URL.
        """
        self._current_proxy: Optional[PROXY] = None
        self._proxies: list = []
        self._proxy_pool: Optional[itertools.cycle]=None
        self._proxy_type: str = 'https'

        proxies = ( proxies
                    or os.environ.get('SCRAPINGHELPER_PROXIES',
                                      default=None) )
        if isinstance(proxies, list):
            self.proxies = proxies
        else:
            if not isinstance(proxies, str):
                proxies = str(proxies)
            if proxies.startswith('file://'):
                filepath = self.normalized_filepath(proxies)
                self.proxies = self.load_proxies(filepath, inplace=False)
            else:
                self.proxies = [proxies]

        self.proxy_pool = itertools.cycle(self.proxies)

    @property
    def proxy_type(self) ->str:
        return self._proxy_type

    @proxy_type.setter
    def proxy_type(self, val):
        if val in ['http', 'https', 'socks4', 'socks5', 'direct', 'quic']:
            self._proxy_type = val
        else:
            raise ValueError('Invalid proxy_type')

    @property
    def proxies(self) ->list:
        return self._proxies

    @proxies.setter
    def proxies(self, val: list):
        if isinstance(val, list) and self._proxies != val:
            self._proxies = val

    @property
    def proxy_pool(self) ->list:
        return self._proxy_pool

    @proxy_pool.setter
    def proxy_pool(self, val: itertools.cycle):
        if isinstance(val, itertools.cycle) and self._proxy_pool != val:
            self._proxy_pool = val

    @property
    def current_proxy(self) ->str:
        if not self._current_proxy:
            self._current_proxy = self.next_proxy(inplace=False)
        return self._current_proxy

    @current_proxy.setter
    def current_proxy(self, val) ->None:
        if self._current_proxy != val:
            self._current_proxy = val

    @classmethod
    def normalized_filepath(cls,
        filepath:str
        ) -> Optional[str]:
        """ normalized filepath.
        Parameters
        ----------
        filepath: str
            if filepath startswith 'file://.',
            expand absolute directory for '.' which is current directory.
        Returns
        -------
        normaized proxies_url:str
        """
        if not filepath:
            return None

        if not isinstance(filepath, str):
            filepath = str(filepath)
        if filepath.startswith('file://.'):
            filepath = filepath.replace('file://.','')
            this_directory = Path(__file__).parent
            filepath = 'file://{}/{}'.format(str(this_directory),filepath)
        return filepath

    def load_proxies(self,
        proxies_url: Optional[str]=None,
        proxy_type: str='https',
        inplace: bool=True,
        ) ->itertools.cycle:
        """Load proxues database from 'proxies_url'.
           and return proxies pool.
        Parameters
        ----------
        proxies_url: str.
            URL of proxies database.
            if proxies_url startswith 'file://.',
            expand absolute directory for '.' which is current directory.
            if proxies_url startswith 'https://',
            read proxies list from URL.

        Returns
        -------
        pool: itertools.cycle
        """

        proxies_url = self.normalized_filepath(proxies_url)
        df = pd.read_csv(proxies_url, names=['proxy'], header=None)
        df['proxy'] = df['proxy'].astype(str)
        proxies =  [ PROXY(x, proxy_type).proxy_url
                          for x in df['proxy'].values.tolist()]
        if inplace:
            self.proxies = proxies
            self.proxy_type = proxy_type
            self.proxy_pool = itertools.cycle(self.proxies)
        else:
            return proxies

    def random_proxy(self, inplace=True) ->PROXY:
        proxy = PROXY(random.choice(self.proxies), self.proxy_type)
        if inplace:
            self.current_proxy = proxy
        return proxy

    def next_proxy(self, inplace=True) ->PROXY:
        proxy =  PROXY(next(self.proxy_pool), self.proxy_type)
        if inplace:
            self.current_proxy = proxy
        return proxy

    def get_proxy(self, rotate: ProxyRotate=ProxyRotate.NEXT) ->PROXY:
        dispatch = { ProxyRotate.NEXT: self.next_proxy,
                     ProxyRotate.RANDOM: self.random_proxy,
                     ProxyRotate.KEEP: lambda : self.current_proxy, }

        if rotate in dispatch:
            return dispatch[rotate]()
        else:
            return None
