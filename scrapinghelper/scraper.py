import time
import ipaddress
from pathlib import Path
from typing import Any, Optional, Union, List, NamedTuple
#
import numpy as np
import pandas as pd
import requests
from requests_html import HTMLSession, AsyncHTMLSession, HTML
from .logging import logger, LogConfig
from .url import URL

class WebScraperException(BaseException):
    pass

class WebScraperCantFind(WebScraperException):
    pass

class TAG_LINK(NamedTuple):
    text: str
    link: Union[URL,str]

class Scraper(object):
    __user_agent_count=10000

    def __init__(self,
                 timeout: int=0,
                 sleep: int=10,
                 max_count: int= 5,
                 max_user_agents: int=10,
                 headers: Optional[dict]=None,
                 logconfig: Optional[LogConfig]=None,
        ):
        """
        Pameters
        --------
        timeout: int
            if provided, of how many long to wait after initial render.
        sleep: int
            if provided, of how many long to sleep after initial render.
        max_user_agents: int
            The number of user_agents to keep in memory. default is 10.
        headers: dict
            request headers. default is automaticaly generated.
        logconfig: LogConfig
            if provided, configure for loguru.

    If just ``sleep`` is provided, the rendering will wait *n* seconds, before
    returning.
        """
        self.timeout = timeout
        self.sleep = sleep
        self.max_count = max_count
        self.columns = list()
        self.values = list()
        self.df = pd.DataFrame()
        self.user_agents = pd.DataFrame()
        self.max_user_agents = max_user_agents
        self.session = None
        self.response = None
        self.headers = headers or {
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "image/webp,image/apng,*/*;q=0.8,"
                    "application/signed-exchange;v=b3;q=0.9"),
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": self.get_random_user_agent(),
            }

        if logconfig:
            logger.remove()
            logger.configure(**(logconfig.config()))
            logger.debug(f'LOG configure: {logconfig}')
        else:
            logger.disable(__name__)

    def get_random_user_agent(self) ->str:
        if self.user_agents.empty:
            data_file  = Path(__file__).parent / 'data/user_agents.csv'
            skip=np.random.randint(1,int(self.__user_agent_count/2))
            if ( skip + self.max_user_agents ) >= self.__user_agent_count:
                skip = 0
            self.user_agents = pd.read_csv(data_file,
                                        header=[0],
                                        skiprows=skip,
                                        nrows=self.max_user_agents)
            self.max_user_agents = len(self.user_agents)
        choose_idx = int(np.random.choice(self.max_user_agents,
                                          replace=True, size=1))
        return self.user_agents.iloc[choose_idx, 1]

    def get_random_ipv4(self) ->str:
        MAX_IPV4 = ipaddress.IPv4Address._ALL_ONES  # 2 ** 32 - 1
        return  ipaddress.IPv4Address._string_from_ip_int(
            np.random.randint(0, MAX_IPV4)
        )

    def get_random_ipv6(self) ->str:
        MAX_IPV6 = ipaddress.IPv6Address._ALL_ONES  # 2 ** 128 - 1
        return ipaddress.IPv6Address._string_from_ip_int(
            np.random.randint(0, MAX_IPV6)
        )

    async def request_async(self,
                url: URL,
                timeout: int=0,
                sleep: int=0,
                max_count: int=0,
                user_agent: Optional[str]=None,
                **kwargs: Any,
        ):
        self.timeout = timeout or self.timeout
        self.sleep = sleep or self.sleep
        self.max_count = max_count or self.max_count
        self.url = url

        if not user_agent:
            headers = self.headers
        elif user_agent == 'random':
            headers = {'User-Agent': self.get_random_user_agent() }
        try:
            self.session = AsyncHTMLSession()
            self.session.headers.update(self.headers)
            logger.debug(f'URL: {url}')
            self.response = await self.session.get(url, **kwargs)
            logger.debug(f'response status_code: {self.response.status_code}')
            self.response.html.arender(
                timeout=self.timeout,
                sleep=random.randint(2,self.sleep))
            return self.response
        except requests.exceptions.RequestException as e:
            self.logger.exception("request failed")

    def request(self,
                url: URL,
                timeout: int=0,
                sleep: int=0,
                max_count: int=0,
                user_agent: Optional[str]=None,
                **kwargs: Any,
        ):
        self.timeout = timeout or self.timeout
        self.sleep = sleep or self.sleep
        self.max_count = max_count or self.max_count
        self.url = url

        if not user_agent:
            headers = self.headers
        elif user_agent == 'random':
            headers = {'User-Agent': self.get_random_user_agent() }

        try:
            self.session = HTMLSession()
            self.session.headers.update(self.headers)
            logger.debug(f'URL: {url}')
            self.response = self.session.get(url, **kwargs)
            logger.debug(f'response status_code: {self.response.status_code}')
            self.response.html.render(
                timeout=self.timeout,
                sleep=np.random.randint(2,self.sleep))
            return self.response
        except requests.exceptions.RequestException as e:
            self.logger.exception("request failed")

    def ommit_char(self,
        values: str,
        omits: str,
        )-> str:
            omit_map = ((x, '') for x in omits)
            for n in range(len(values)):
                values[n] = values[n].replace(*omit_map)
            return values

    def get_texts(self,
        html: HTML,
        selector: Union[list, str]=['table', 'tr'],
        split: str='\n',
        index: int=0,
        headers: Optional[List[str]]=None,
        **kwargs: Any,
        )->list:
        """get text from specified selector of HTML object.
        Parameters
        ----------
        html: HTML
            HTML object of requests_html
        selector: str
            CSS Selector or tag. default is ['table','tr']
        Returns
        ------
        list of result: str
        """

        if isinstance(selector, str):
            selector = [selector]

        elements = html.find(selector[0], **kwargs)
        for select in selector[-1:]:
            elements = elements[0].find(select, **kwargs)

        if hasattr(elements, '__iter__'):
            contents = [ x.text.split(split) for x in elements ]
        else:
            contents = [ elements.text.split(split) ]
        return contents


    def get_links(self,
        html: HTML,
        selector: str='a',
        startswith: Optional[Union[list,str]] = None,
        endswith: Optional[Union[list,str]] = None,
        containing: Optional[Union[list,str]] = None,
        **kwargs: Any,
        ) -> list:
        """get links from contents of HTML object.
        Parameters
        ----------
        html: HTML
            HTML object of requests_html
        selector: str
            CSS Selector or tag. default is 'a'
        startswith: Optional[Union[list,str]] = None
            if startswith passed, return only startswith for basename of url.
            i.e.: link is 'http://example.com/example/sample.txt'
                  return this link when passed startswith('s').
        endswith: Optional[Union[list,str]] = None
            if endswith passed, return only endswith for basename of url.
            i.e.: link is 'http://example.com/example/sample.txt'
                  return this link when passed endswith('.txt').
        containing: Optional[Union[list,str]] = None
            if containing passed, return only word contain in path of url.
            i.e.: link is 'http://example.com/example/sample.txt'
                  return this link when passed containing('example').
        Returns
        ------
        list of result: str
        """

        if startswith and isinstance(startswith, str):
            startswith = [startswith]
        if endswith and isinstance(endswith, str):
            endswith = [endswith]
        if containing and isinstance(containing, str):
            endswith = [endswith]
        links = list()
        for e in html.find(selector, **kwargs):
            for link in e.links:
                url = URL(link)
                if startswith and not any(url.basename.startswith(x) for x in startswith):
                    continue
                if endswith and not any(url.basename.endswith(x) for x in endswith):
                    continue
                if containing and not any(x in url.basename for x in containing):
                    continue
                try:
                    links.append(TAG_LINK(text=e.text, link=URL(link)))
                except:
                    pass

        return links

    def get_filename(self,
        url: Union[URL, str],
        replace: Optional[Union[list,tuple]]=None,
        )-> bool:
        if hasattr(url, 'is_valid') and url.is_valid:
            filename = url.basename
        else:
            try:
                filename = URL(url).basename
            except:
                filename = None

        if filename and replace:
            filename = filename.replace( replace )

        return filename

    def download_file(self,
        url: Union[URL, str],
        filename: Optional[str]=None,
        sleep: int=0,
        user_agent: Optional[str]=None,
        ) -> bool:
        """download file from url
        Parameters
        ----------
        url: Union[URL,str]
            you must set url.
        filename: str
            if not set, using basename of deccoded url.
        sleep: int
            if not set, using sleep time of session.
        user_agent: str
            if not set, using user_agent of session.
            if set as 'random', using random user_agent.

        Return
        download status: bool
        """

        if not hasattr(url, 'is_valid'):
            url = URL(url)

        if not url.is_valid:
            raise WebScraperException('Invalid url')

        if not filename:
            filename = url.basename

        if not user_agent:
            headers = self.headers
        elif user_agent == 'random':
            headers = {'User-Agent': self.get_random_user_agent() }
        else:
            headers = {'User-Agent': user_agent }

        sleep = sleep or self.sleep
        try:
            if sleep:
                time.sleep(sleep)
            data = requests.get(url.url, headers=headers)
            with open(filename, 'wb') as fp:
                fp.write(data.content)
            return True
        except:
            raise WebScraperException('download failed')

    def add_df(self, values, columns, omits = None):
            if omits is not None:
                values = self.omit_char(values,omits)
                columns = self.omit_char(columns,omits)

            # Since Pandas 1.3.0
            df = pd.DataFrame(values,index=columns)._maybe_depup_names(columns)
            self.df = pd.concat([self.df,df.T])

