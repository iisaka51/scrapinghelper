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
from requests_html import (
    HTML, HTMLResponse, Element, MaxRetries, PyQuery
)
import requests_html
from .logging import logger, LogConfig
from .url import URL
from .proxy import ProxyManager, ProxyRotate, PROXY
from .user_agents import UserAgent
from .user_agents import user_agent as useragent_manager

DEFAULT_USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
DEFAULT_BROWSER_ARGS = '--no-sandbox -ignore-certificate-errors'

class WebScraperException(BaseException):
    pass

class WebScraperNotFound(WebScraperException):
    pass

class TAG_LINK(NamedTuple):
    text: str
    link: Union[URL,str]

def user_agent(style:Optional[str]=None) ->str:
    # style is always ignore. just for compatibility.
    try:
        return useragent_manager.first_user_agent
    except:
        return DEFAULT_USER_AGENT

def _gen_browser_args(
        default_args: str = DEFAULT_BROWSER_ARGS,
        proxy_server:Optional[str]=None
    )->list:
    default_args = '{} {}'.format(
                                default_args,
                                os.environ.get('SCRAPINGHELPER_BROWSER_ARGS',
                                               default=DEFAULT_BROWSER_ARGS ) )
    browser_args: list = list(dict.fromkeys(default_args.split(' ')))

    if proxy_server:
        browser_args += ["--proxy-server={}".format(proxy_server) ]

    return browser_args

class HTMLSession(requests_html.BaseSession):

    def __init__(self,
            proxy_server: Optional[str]=None,
            browser_args: str = DEFAULT_BROWSER_ARGS,
            **kwargs:Any
        )->None:
        self._proxy_server = None

        if proxy_server:
            self.proxy_server = proxy_server

        kwargs['browser_args'] = _gen_browser_args(browser_args, proxy_server)

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

    def close(self) ->None:
        """ If a browser was created close it first. """
        if hasattr(self, "_browser"):
            self.loop.run_until_complete(self._browser.close())
        super().close()

class AsyncHTMLSession(requests_html.BaseSession):

    def __init__(self,
            loop=None, workers=None,
            mock_browser: bool = True,
            browser_args: str = DEFAULT_BROWSER_ARGS,
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

        kwargs['browser_args'] = _gen_browser_args(browser_args, proxy_server)

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

    async def close(self) ->None:
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
                 *,
                 browser_args: str = DEFAULT_BROWSER_ARGS,
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

        browser_args: str
            browser lunch option.

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
        self.browser_args = browser_args
        self.columns: list = list()
        self.values: list = list()
        self.df: pd.DataFrame = pd.DataFrame()
        self.session: Union[HTMLSession, AsyncHTMLSession] = None
        self.response: HTMLResponse = None
        self.proxy_manager: ProxyManager = ProxyManager(proxies)

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
        return self.user_agent.get_random_user_agent()

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

    def random_wait(self, sleep: int=0):
        sleep = sleep or self.sleep
        time.sleep(np.random.randint(2,sleep))

    def load_proxies( self,
        proxies: Optional[Union[list,str]]=None):
        """ load proxies from URL/file/list.
        proxies: proxies: Optional[Union[list,str]]=None
            list of proxies
            if proxies startswith 'file://', load proxies from file.
            if proxies startswith 'https://', load proxies from URL.
        """
        _ = self.proxy_manager.load_proxies(proxies)

    def session_close(self) ->None:
        if self.session:
            self.session.close()
            self.session = None

    async def request_async(self,
                url: URL,
                timeout: int=0,
                sleep: int=0,
                user_agent: Optional[str]=None,
                proxy_rotate: ProxyRotate=ProxyRotate.NO_PROXY,
                render: bool=True,
                render_kwargs: dict={'keep_page': False},
                **kwargs: Any,
        ) ->HTMLResponse:
        self.timeout = timeout or self.timeout
        self.sleep = sleep or self.sleep
        self.url = url

        if not user_agent:
            headers = self.headers
        elif user_agent == 'random':
            headers = {'User-Agent': self.get_random_user_agent() }

        if proxy_rotate != ProxyRotate.NO_PROXY:
            self.session_close()

        if not self.session:
            proxy_server = self.proxy_manager.get_proxy(proxy_rotate)
            proxy_server = proxy_server.proxy_map['https'] if proxy_server else None
            self.session = AsyncHTMLSession( browser_args = self.browser_args,
                                             proxy_server=proxy_server )

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
                                sleep=np.random.randint(2,self.sleep),
                                **render_kwargs,
                                )
            return response

        self.response = self.session.run(get_page)[0]
        return self.response

    def request(self,
                url: URL,
                timeout: int=0,
                sleep: int=0,
                user_agent: Optional[str]=None,
                proxy_rotate: ProxyRotate=ProxyRotate.NO_PROXY,
                render: bool=True,
                render_kwargs: dict={'keep_page': False},
                **kwargs: Any,
        ) ->HTMLResponse:
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

            if not self.session:
                proxy_server = self.proxy_manager.get_proxy(proxy_rotate)
                proxy_server = proxy_server.proxy_map['https'] if proxy_server else None
                self.session = HTMLSession( browser_args = self.browser_args,
                                            proxy_server=proxy_server )

            self.session.headers.update(self.headers)
            logger.debug('URL: {}'.format(url))
            proxy= self.proxy_manager.get_proxy(proxy_rotate)
            proxy_map = proxy.proxy_map if proxy else None
            self.response = self.session.get(url, proxies=proxy_map, **kwargs)
            logger.debug('response status_code: {}'.format(self.response.status_code))
            if render:
                render_kwargs['timeout'] = render_kwargs.get('timtout',
                                                              self.timeout )
                sleep = render_kwargs.get('sleep', self.sleep)
                render_kwargs['sleep'] = np.random.randint(2,sleep)
                self.response.html.render( **render_kwargs )
            return self.response

        except requests.exceptions.RequestException as e:
            logger.exception("request failed")

    def get_texts(self,
        selector: Union[list, str]=['table', 'tr'],
        html: Optional[HTML]=None,
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

        html = html or self.response.html

        elements = html.find(selector[0], **kwargs)
        for select in selector[-1:]:
            if select == selector[0]:
                continue
            elements = elements[0].find(select, **kwargs)

        if hasattr(elements, '__iter__'):
            contents = [ x.text.split(split) for x in elements ]
        else:
            contents = [ elements.text.split(split) ]
        return contents


    def get_links(self,
        selector: str='a',
        startswith: Optional[Union[list,str]] = None,
        endswith: Optional[Union[list,str]] = None,
        containing: Optional[Union[list,str]] = None,
        html: Optional[HTML]=None,
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
        html = html or self.response.html

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
        replace: dict={},
        )-> bool:
        """ extract filename from URL, and convert filename if necessary """

        if hasattr(url, 'is_valid') and url.is_valid:
            filename = url.basename
        else:
            try:
                filename = URL(url).basename
            except:
                filename = None

        if filename and replace:
            [filename := filename.replace(old, new)
                        for old, new in replace.items()]

        return filename

    def download_file(self,
        url: Union[URL, str],
        filename: str='',
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
