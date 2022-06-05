import re

from urllib.parse import (
    ParseResult,
    urlparse, parse_qsl, urlencode, quote, unquote,
 )
from typing import Any, Optional, Tuple, Union

ip_middle_octet = r"(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5]))"
ip_last_octet = r"(?:\.(?:0|[1-9]\d?|1\d\d|2[0-4]\d|25[0-5]))"

__regex = re.compile(  # noqa: W605
    r"^"
    # protocol identifier
    r"(?:(?:https?|ftp)://)"
    # user:pass authentication
    r"(?:[-a-z\u00a1-\uffff0-9._~%!$&'()*+,;=:]+"
    r"(?::[-a-z0-9._~%!$&'()*+,;=:]*)?@)?"
    r"(?:"
    r"(?P<private_ip>"
    # IP address exclusion
    # private & local networks
    r"(?:(?:10|127)" + ip_middle_octet + r"{2}" + ip_last_octet + r")|"
    r"(?:(?:169\.254|192\.168)" + ip_middle_octet + ip_last_octet + r")|"
    r"(?:172\.(?:1[6-9]|2\d|3[0-1])" + ip_middle_octet + ip_last_octet + r"))"
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
    r"" + ip_middle_octet + r"{2}"
    r"" + ip_last_octet + r")"
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
    r"$",
    re.UNICODE | re.IGNORECASE
)

pattern = re.compile(__regex)

def url_validator(value, public=False):
    """
    Return whether or not givven value is a valid URL.
    If the value is valid URL this function returns ``True``,
    otherwise ``False```.

    This validator is based on `validator of dperini`
    See Also: https://gist.github.com/dperini/729294

    Examples::

        >>> url('http://example.com')
        True

        >>> url('ftp://example.com')
        True

        >>> url('http://example.d')
        False

        >>> url('http://10.0.0.1')
        True

        >>> url('http://10.0.0.1', public=True)
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
    return result

class URL(object):
    __default_safe: str = ':/?&@=#%'
    def __init__(self,
        url: Optional[str]=None,
        safe: Optional[str]=None,
    ):
        f"""
        The class for URL.
        The url is quoted The %-escapes all characters.

        paramurl: str
            The any URL
        safe: str
            the additional safe chars.
            default safe chars is {self.__default_safe}
        """

        self.safe = safe or self.__default_safe
        if url:
            self.url = quote(url, safe=self.safe)
        else:
            self.url = ''
        ( self.is_valid,
            self.scheme, self.netloc,
            self.username, self.password, self.hostname, self.port,
            self.path, self.params, self.query, self.fragment
        ) = self.__validator(url)

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
        >>> from scrapper_tools import URL
        >>> url = URL()
        >>> url.validator('http://example.com')
        True

        >>> url.validator('ftp://example.com')
        True

        >>> url('http://10.0.0.1')
        True

        """
        return self.__validator(url)[0]

    def __validator(self,
        url: str
    ) -> Tuple[bool,
               str, str,
               Optional[str], Optional[str], str, Optional[str],
               str, str, str, str]:

        try:
            v = urlparse(url)
            val = ( False if not url_validator(url) else True,
                    v.scheme, v.netloc,
                    v.username, v.password, v.hostname, v.port,
                    v.path, v.params, v.query, v.fragment)
        except:
            v = False
            val = (v, '', '', '',
                      None, None, '', None, '', '', '')
        return val

    def __repr__(self) -> str:
        return str(self.url)

    def decode(self,
            url: Optional[str]=None) -> str:
        """ Take a decoded url
        Parameters
        ----------
        url: str
            The input url.

        Returns
        -------
        decoded_url: str
        """

        if not url:
            url = self.url
        return unquote(url)

    def encode(self,
            url: Optional[str]=None) -> str:
        """ Take a decoded url
        Parameters
        ----------
            url: str
                The input url.
        """
        if not url:
            url = self.url
            val = ( f'{self.scheme}://{self.netloc}{self.path}{self.query}' )
        return quote(url, safe=self.safe)

    def set_query_val(self,
            param: str,
            value: Union[str, int, float],
            url: Optional[str]=None,
            update=False,
            use_https=False
        ):
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
