import os
import time
import asyncio
import ipaddress
import pyppeteer
from pathlib import Path
import itertools
from typing import Any, Optional, Union, NamedTuple
#
import numpy as np
import pandas as pd
import requests
from requests_html import HTML, HTMLResponse, Element
import requests_html
from .logging import logger, LogConfig
from .url import URL
from .proxy import ProxyManager, ProxyRotate
from .user_agents import UserAgent
from .user_agents import user_agent as useragent_manager

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'

class WebScraperException(BaseException):
    pass

class WebScraperCantFind(WebScraperException):
    pass

class TAG_LINK(NamedTuple):
    text: str
    link: Union[URL,str]

def user_agent(style=None):
    # style is always ignore. just for compatibility.
    return useragent_manager.first_user_agent

def _gen_browser_args(
        proxy_server:Optional[str]=None
    )->list:
    browser_args = os.environ.get('SCRAPINGHELPER_BROWSER_ARGS',
                       default='--no-sandbox -ignore-certificate-errors' )
    browser_args = browser_args.split(' ')

    if proxy_server:
        browser_args += ["--proxy-server={}".format(proxy_server) ]

    return browser_args

class HTMLSession(requests_html.BaseSession):

    def __init__(self,
            proxy_server: Optional[str]=None,
            **kwargs:Any
        )->None:
        self._proxy_server = None

        if proxy_server:
            self.proxy_server = proxy_server

        browser_args = _gen_browser_args(proxy_server)
        kwargs['browser_args'] = browser_args

        super().__init__(**kwargs)

    @property
    def proxy_server(self):
        return self._proxy_server

    @proxy_server.setter
    def proxy_server(self, val):
        if self._proxy_server != val:
            self._proxy_server = val

    @property
    def browser(self):
        if not hasattr(self, "_browser"):
            self.loop = asyncio.get_event_loop()
            if self.loop.is_running():
                raise RuntimeError("Cannot use HTMLSession within an existing event loop. Use AsyncHTMLSession instead.")
            self._browser = self.loop.run_until_complete(super().browser)
        return self._browser

    def close(self):
        """ If a browser was created close it first. """
        if hasattr(self, "_browser"):
            self.loop.run_until_complete(self._browser.close())
        super().close()

class AsyncHTMLSession(requests_html.BaseSession):

    def __init__(self,
            loop=None, workers=None,
            mock_browser: bool = True,
            proxy_server: Optional[str]=None,
            *args:Any, **kwargs:Any
        )-> None:
        """ Set or create an event loop and a thread pool.

            :param loop: Asyncio loop to use.
            :param workers: Amount of threads to use for executing async calls.
                If not pass it will default to the number of processors on the
                machine, multiplied by 5. """
        self._proxy_server = None

        if proxy_server:
            self.proxy_server = proxy_server

        browser_args = _gen_browser_args(proxy_server)
        kwargs['browser_args'] = browser_args

        super().__init__(*args, **kwargs)

    @property
    def proxy_server(self):
        return self._proxy_server

    @proxy_server.setter
    def proxy_server(self, val):
        if self._proxy_server != val:
            self._proxy_server = val

    def request(self, *args, **kwargs):
        """ Partial original request func and run it in a thread. """
        func = partial(super().request, *args, **kwargs)
        return self.loop.run_in_executor(self.thread_pool, func)

    async def close(self):
        """ If a browser was created close it first. """
        if hasattr(self, "_browser"):
            await self._browser.close()
        super().close()

    def run(self, *coros):
        """ Pass in all the coroutines you want to run, it will wrap each one
            in a task, run it and wait for the result. Return a list with all
            results, this is returned in the same order coros are passed in. """
        tasks = [
            asyncio.ensure_future(coro()) for coro in coros
        ]
        done, _ = self.loop.run_until_complete(asyncio.wait(tasks))
        return [t.result() for t in done]


class Scraper(object):
    def __init__(self,
                 timeout: int=0,
                 sleep: int=10,
                 keep_user_agents: int=50,
                 datapath: Optional[str]=None,
                 headers: Optional[dict]=None,
                 proxies: Optional[Union[list,str]]=None,
                 logconfig: Optional[LogConfig]=None,
        ):
        """
        Pameters
        --------
        timeout: int
            if provided, of how many long to wait after initial render.

        sleep: int
            if provided, of how many long to sleep after initial render.

        keep_user_agents: int
            The number of user_agents to keep in memory. default is 50.
            if 0 passed for keep_user_agents, all data will be kept.

        datapath: str
            (option) The CSV filename of user_agents datasets from 51degrees.com.
        headers: dict
            request headers. default is automaticaly generated.

        proxies: proxies: Optional[Union[list,str]]=None
            list of proxies
            if proxies startswith 'file://', load proxies from file.
            if proxies startswith 'https://', load proxies from URL.

        logconfig: LogConfig
            if provided, configure for loguru.

    If just ``sleep`` is provided, the rendering will wait *n* seconds, before
    returning.
        """
        self.timeout = timeout
        self.sleep = sleep
        self.columns = list()
        self.values = list()
        self.df = pd.DataFrame()
        self.session = None
        self.response = None
        self.proxy_manager = ProxyManager(proxies)

        self.user_agent = useragent_manager
        self.user_agent.load_datafile(keep_user_agents, datapath)
        self.headers = headers or {
                "Accept": (
                    "text/html,application/xhtml+xml,"
                    "application/xml;q=0.9,"
                    "image/webp,image/apng,*/*;q=0.8,"
                    "application/signed-exchange;v=b3;q=0.9"),
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "en",
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": self.user_agent.get_random_user_agent(),
            }

        if logconfig:
            logger.remove()
            logger.configure(**(logconfig.config()))
            logger.debug('LOG configure: {}'.format(logconfig))
        else:
            logger.disable(__name__)

    def get_random_user_agent(self) -> str:
        return self.user_agent.get_random_user_agent

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

    def load_proxies( self,
        proxies: Optional[Union[list,str]]=None):
        """ load proxies from URL/file/list.
        proxies: proxies: Optional[Union[list,str]]=None
            list of proxies
            if proxies startswith 'file://', load proxies from file.
            if proxies startswith 'https://', load proxies from URL.
        """
        _ = self.proxy_manager.load_proxies(proxies)

    def session_close(self):
        if self.session:
            self.session.close()
            self.session = None

    async def request_async(self,
                url: URL,
                timeout: int=0,
                sleep: int=0,
                user_agent: Optional[str]=None,
                proxy_rotate: ProxyRotate=ProxyRotate.NO_PROXY,
                render=True,
                **kwargs: Any,
        ):
        self.timeout = timeout or self.timeout
        self.sleep = sleep or self.sleep
        self.url = url

        if not user_agent:
            headers = self.headers
        elif user_agent == 'random':
            headers = {'User-Agent': self.get_random_user_agent() }

        if proxy_rotate != ProxyRotate.NO_PROXY:
            self.session_close()

        self.session = self.session or AsyncHTMLSession(
                    proxy_server=self.proxy_manager.get_proxy(proxy_rotate))
        self.session.headers.update(self.headers)
        logger.debug('URL: {}'.format(url))

        async def get_page():
            proxy = self.proxy_manager.get_proxy(proxy_rotate)
            proxy_map = proxy.proxy_map if proxy else None
            response = await self.session.get(url, proxies=proxy_map, **kwargs)
            logger.debug('response status_code: {}'.format(response.status_code))
            if render:
                await response.html.arender(
                                timeout=self.timeout,
                                sleep=np.random.randint(2,self.sleep))
            return response

        self.response = self.session.run(get_page)[0]
        return self.response

    def request(self,
                url: URL,
                timeout: int=0,
                sleep: int=0,
                user_agent: Optional[str]=None,
                proxy_rotate: ProxyRotate=ProxyRotate.NO_PROXY,
                render=True,
                **kwargs: Any,
        ):
        """request get page from URL
        """
        self.timeout = timeout or self.timeout
        self.sleep = sleep or self.sleep
        self.url = url

        if not user_agent:
            headers = self.headers
        elif user_agent == 'random':
            headers = {'User-Agent': self.get_random_user_agent() }

        try:
            if proxy_rotate != ProxyRotate.NO_PROXY:
                self.session_close()

            self.session = self.session or HTMLSession(
                    proxy_server=self.proxy_manager.get_proxy(proxy_rotate))
            self.session.headers.update(self.headers)
            logger.debug('URL: {}'.format(url))
            proxy= self.proxy_manager.get_proxy(proxy_rotate)
            proxy_map = proxy.proxy_map if proxy else None
            self.response = self.session.get(url, proxies=proxy_map, **kwargs)
            logger.debug('response status_code: {}'.format(self.response.status_code))
            if render:
                self.response.html.render(
                    timeout=self.timeout,
                    sleep=np.random.randint(2,self.sleep))
            return self.response

        except requests.exceptions.RequestException as e:
            logger.exception("request failed")

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
            containing = [containing]
        links = list()
        for e in html.find(selector, **kwargs):
            for link in e.links:
                url = URL(link)
                if startswith and not any(url.basename.startswith(x) for x in startswith):
                    continue
                if endswith and not any(url.basename.endswith(x) for x in endswith):
                    continue
                if containing and not any(x in url.decode() for x in containing):
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

