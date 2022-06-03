from urllib.parse import (
    ParseResult,
    urlparse, parse_qsl, urlencode, quote, unquote,
 )
from typing import Any, Optional, Tuple, Union
from validators.url import url as url_validator

class URL(object):
    __default_safe: str = ':/?&@=#%'
    def __init__(self,
        url: Optional[str]=None,
        safe: Optional[str]=None,
    ):
        f"""
        The class for URL.
        The url is quoted The %-escapes all characters.

        Parameters
        ----------
        url: str
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
