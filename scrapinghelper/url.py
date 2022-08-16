import os
import re

from urllib.parse import (
    ParseResult,
    urlparse, parse_qsl, urlencode, quote, unquote,
 )
from typing import Any, Optional, Tuple, Union, NamedTuple

IP_MIDDLE_OCTET = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
IP_LAST_OCTET = r"(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))"

URL_PATTERN = ( # noqa: W605
    # protocol identifier
    r"(?:(?:https?|ftp)://)"
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
    # excludes loopback network 0.0.0.0
    # excludes reserved space >= 224.0.0.0
    # excludes network & broadcast addresses
    # (first & last IP address of each class)
    r"(?P<public_ip>"
    r"(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])"
    r"" + IP_MIDDLE_OCTET + r"{2}"
    r"" + IP_LAST_OCTET + r")"
    r"|"
    # IPv6 RegEx from https://stackoverflow.com/a/17871737
    r"\[("
    # 1:2:3:4:5:6:7:8
    r"([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|"
    # 1::                              1:2:3:4:5:6:7::
    r"([0-9a-fA-F]{1,4}:){1,7}:|"
    # 1::8             1:2:3:4:5:6::8  1:2:3:4:5:6::8
    r"([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|"
    # 1::7:8           1:2:3:4:5::7:8  1:2:3:4:5::8
    r"([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|"
    # 1::6:7:8         1:2:3:4::6:7:8  1:2:3:4::8
    r"([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|"
    # 1::5:6:7:8       1:2:3::5:6:7:8  1:2:3::8
    r"([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|"
    # 1::4:5:6:7:8     1:2::4:5:6:7:8  1:2::8
    r"([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|"
    # 1::3:4:5:6:7:8   1::3:4:5:6:7:8  1::8
    r"[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|"
    # ::2:3:4:5:6:7:8  ::2:3:4:5:6:7:8 ::8       ::
    r":((:[0-9a-fA-F]{1,4}){1,7}|:)|"
    # fe80::7:8%eth0   fe80::7:8%1
    # (link-local IPv6 addresses with zone index)
    r"fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|"
    r"::(ffff(:0{1,4}){0,1}:){0,1}"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # ::255.255.255.255   ::ffff:255.255.255.255  ::ffff:0:255.255.255.255
    # (IPv4-mapped IPv6 addresses and IPv4-translated addresses)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|"
    r"([0-9a-fA-F]{1,4}:){1,4}:"
    r"((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}"
    # 2001:db8:3:4::192.0.2.33  64:ff9b::192.0.2.33
    # (IPv4-Embedded IPv6 Address)
    r"(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])"
    r")\]|"
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
    # resource path
    r"(?:/[-a-z\u00a1-\uffff\U00010000-\U0010ffff0-9._~%!$&'()*+,;=:@/]*)?"
    # query string
    r"(?:\?\S*)?"
    # fragment
    r"(?:#\S*)?"
)

pattern = re.compile( r"^" + URL_PATTERN + r"$", re.UNICODE | re.IGNORECASE)

def url_validator(value, public=False):
    """
    Return whether or not givven value is a valid URL.
    If the value is valid URL this function returns ``True``,
    otherwise ``False```.

    This validator is based on `validator of dperini`
    See Also: https://gist.github.com/dperini/729294

    Examples::

        >>> url_validator('http://example.com')
        True

        >>> url_validator('ftp://example.com')
        True

        >>> url_validator('http://example.d')
        False

        >>> url_validator('http://10.0.0.1')
        True

        >>> url_validator('http://10.0.0.1', public=True)
        False

    Parameters
    ----------
    value: str
        URL address string to validate
    public: bool
         If set True to only allow a public IPAddress. (default is False)

    Returns
    -------
    result: bool
        Return ``True`` if the value is valid URL, otherwise ``False``
    """

    check = pattern.match(value)
    if public:
        result = check and not any( check.groupdict().get(key)
                                    for key in ('private_ip', 'private_host'))
    else:
        result = check

    result = True if result else False
    return result


def remove_urls(
        text: str,
        endswith: str ='',
    ) -> str:
    """ Remove any url in the text.
    Parameters
    ----------
        text: str
             The text to remove urls.
        endswith: str
             If set, only remove the URLs that finish with that
             regular expression.
             default is all the URLs are remvoed.
    Returns
    -------
        removed_text: str
            The same text but without urls.
    """
    return replace_urls(text, '', endswith)

def replace_urls(
        text: str,
        replace: str,
        endswith: str = '',
    ) -> str:
    """ Replace all the URLs with path by a text.
    Patameters
    ----------
        text: str
            The text to replace.
        replace: str
            The text to replace with.
        endswith: str
            A regular expression which the URL has to finish with.
            default is replace all the URLs.
    Returns
    -------
        removed_text: str
    Known BUGS
    ----------
        This function is not perfect.
    """
    pattern = re.compile( URL_PATTERN + endswith, re.UNICODE | re.IGNORECASE)
    matches = list(re.finditer(pattern, text))
    matches.reverse()
    for match in matches:
        start, end = match.span()[0], match.span()[1]
        text = text[:start] + replace + text[end:]
    return text


class ResultURLValidator(NamedTuple):
    url: str
    is_valid: bool
    scheme: str
    netloc: str
    username: Optional[str]
    password: Optional[str]
    hostname: str
    port: Optional[str]
    path: str
    params: str
    query: str
    fragment: str
    basename: str


class URL(object):
    __default_safe: str = ':/?&@=#%'
    def __init__(self,
        url: Optional[str]=None,
        do_quote: bool=True,
        safe: Optional[str]=None,
    ):
        f"""
        The class for URL.
        The url is quoted The %-escapes all characters.

        Parameters
        ----------
        url: str
            The any URL
        do_quote: bool
            Replace special characters in string using the %xx escape.
            default is ``True``
        safe: str
            the additional safe chars.
            default safe chars is {self.__default_safe}

        Return
        ------
        url: str
            The url is quoted he %-escapes all characters.
        """
        self.url: str
        self.is_valid: bool
        self.scheme: str
        self.netloc: str
        self.username: Optional[str]
        self.password: Optional[str]
        self.hostname: str
        self.port: Optional[str]
        self.path: str
        self.params: str
        self.query: str
        self.fragment: str
        self.basename: str

        self.safe = safe or self.__default_safe
        if url:
            if do_quote:
                self.url = quote(url, safe=self.safe)
            else:
                self.url = url
        else:
            self.url = None

        self.validate = self.__validator(self.url)
        self.__dict__.update(self.validate._asdict())

    def validator(self, url: str) -> bool:
        """
        Return whether or not given value is a valid URL
        If the value is valid URL this function returns ``True``,
        otherwise ``False``.

        Parameters
        ----------
        url: str
            The input url

        Examples
        --------
        >>> from scrapinghelper import URL
        >>> url = URL()
        >>> url.validator('http://example.com')
        True

        >>> url.validator('ftp://example.com')
        True

        >>> url('http://10.0.0.1')
        True

        """
        return self.__validator(url).is_valid

    def __validator(self,
        url: str
    ) -> ResultURLValidator:

        try:
            v = urlparse(url)
            _is_valid =  url_validator(url)
            _scheme = v.scheme
            _netloc = v.netloc
            _username = v.username
            _password = v.password
            _hostname =  v.hostname
            _port = v.port
            _path = v.path
            _params = v.params
            _query = v.query
            _fragment = v.fragment
            _basename = os.path.basename(unquote(v.path))
        except:
            _is_valid = False
            _scheme = ''
            _netloc = ''
            _username = None
            _password = None
            _hostname =  ''
            _port = None
            _path = ''
            _params = ''
            _query = ''
            _fragment = ''
            _basename = None

        result = ResultURLValidator(
                    url, _is_valid,
                    _scheme, _netloc,
                    _username, _password, _hostname, _port,
                    _path, _params, _query, _fragment, _basename)

        return result

    @property
    def attrs(self):
        return self.validate._asdict()

    def __repr__(self) -> str:
        return str(self.url)

    def unquote(self,
            url: Optional[str]=None,
            **kwargs: Any,
        ) -> str:
        """ Take a unquoted url
        Parameters
        ----------
        url: str
            The input url.
        **kwrags:
            pass to urllib.parse.unquote

        Returns
        -------
        unquoted_url: str
        """

        if not url:
            url = self.url
        return unquote(url, **kwargs)

    def quote(self,
            url: Optional[str]=None,
            **kwargs: Any,
        ) -> str:
        """ Take a quoted url
        Parameters
        ----------
        url: str
            The input url.
        **kwargs:
            pass to urllib.parse.unquote

        Returns
        -------
        quoted_url: str
        """
        if not url:
            url = self.url
        return quote(url, safe=self.safe, **kwargs)

    # alias names
    encode = quote
    decode = unquote

    def set_query_val(self,
            param: str,
            value: Union[str, int, float],
            url: Optional[str]=None,
            update=False,
            use_https=False
        ) -> str:
        """ Takes a url and changes the value of a query string parameter.
        Parameters
        ----------
        param: str
            The name of the query string parameter that needs to be change
        value: Union[str, int, float]
            The new value for the parameter
        create: bool
            if set to True, will create a new query string parameter.
        url: str
            The input url.
        use_https: bool
             If set to true, will upgrade to HTTPS

        Returns
        -------
        Updated URL: str
        """

        if not url:
            url = self.url
            query = self.query

        if not query:
            if "?" in url:
                query = url.split("?")[1]

        qs_val = dict(parse_qsl(query))
        qs_val[f"{param}"] = value
        new_url = url.split("?")[0] + "?" + urlencode(qs_val)

        if use_https:
            self.scheme = "https"
            new_url = new_url.replace("http://", "https://")

        if update:
            self.url = new_url

        return new_url

    def get_query_val(self,
            param: Optional[str]=None,
            url: Optional[str]=None
        ) -> str:
        """Takes a url and extract value of a query string parameter.

        Parameters
        ----------
        url: str
             The input url.
        param: str
             The name of the query string parameter

        Returns
        -------
        val: str
            extract value of a query string parameter
        """

        if not url:
            url = self.url
            query = self.query

        if not query:
            if "?" in url:
                query = url.split("?")[1]

        query_val = dict(parse_qsl(query))
        return query_val.get(param)

    def strip_query(self,
            url: Optional[str]=None
        ) ->str:
        """Takes a url and strips all query string parameters.
        Parameters
        ----------
        url: Any url like https://example.com/sample?src=git

        Returns
        -------
        full url without queries.:
        """

        if not url:
            self.url = f"{self.scheme}://{self.netloc}{self.path}"
            result = self.url
        else:
            v = urlparse(url)
            result = f"{v.scheme}://{v.netloc}{v.path}"
        return result

    def get_root_address(self,
            url: Optional[str]=None
        ) ->str:
        """Takes a url and strips returns the root url
        Parameters
        ----------
        url: str
             Any url like 'https://example.com/sample?src=git'
        full url without parameters: 'https://example.com/'
        """
        if not url:
            result = f"{self.scheme}://{self.netloc}"
        else:
            v = urlparse(url)
            result = f"{v.scheme}://{v.netloc}"
        return result
