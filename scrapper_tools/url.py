from urllib.parse import (
    ParseResult,
    urlparse, parse_qsl, urlencode, quote, unquote,
 )
from typing import Any, Optional, Tuple
from dataclasses import dataclass, InitVar
from validators.url import url as url_validator

@dataclass
class URL(object):
    url: InitVar[str]=None

    def __post_init__(self, url: str) -> str:
        self.url = quote(url, safe=':/?&@=#%')
        ( self.is_valid,
          self.scheme, self.netloc,
          self.username, self.password, self.hostname, self.port,
          self.path, self.params, self.query, self.fragment
        ) = self.__validator(url)

    def validator(self, url: str) -> bool:
        return self.__validator(url)[0]

    def __validator(self, url: str) -> Tuple[bool,
                                           str, str, str, str, str, str]:

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
        @param url: The input url.
        """
        if not url:
            url = self.url
        return unquote(url)

    def encode(self,
            url: Optional[str]=None) -> str:
        """ Take a decoded url
        @param url: The input url.
        """
        if not url:
            url = self.url
            val = ( f'{self.scheme}://{self.netloc}{self.path}{self.query}' )
        return quote(url, safe=':/?&@=#%')

    def set_query_val(self,
            param,
            value,
            url: Optional[str]=None,
            create=False,
            use_https=False
        ):
        """ Takes a url and changes the value of a query string parameter.
        @param param: The name of the query string parameter
                      that needs to be change
        @param value: The new value for the parameter
        @param create: if set to True, will create a new query string parameter.
        @param url: The input url.
        @param upgrade_https: If set to true, will upgrade to HTTPS
        @return: Updated URL
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

        if create:
            self.query =  urlencode({param: value})
            new_url = url + "?" + self.query

        if use_https:
            self.scheme = "https"
            new_url = new_url.replace("http://", "https://")

        if not url:
            self.url = new_url

        return new_url

    def get_query_val(self,
            param: Optional[str]=None,
            url: Optional[str]=None
        ) -> str:
        """Takes a url and extract value of a query string parameter.
        @param url: The input url.
        @param param: The name of the query string parameter
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
        @param url: Any url like https://example.com/sample?src=git
        @return: full url without parameters:
                 See Also: https://example.com/sample
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
        @param url: Any url like https://example.com/sample?src=git
        @return: full url without parameters: https://example.com/
        """
        if not url:
            result = f"{self.scheme}://{self.netloc}"
        else:
            v = urlparse(url)
            result = f"{v.scheme}://{v.netloc}"
        return result
