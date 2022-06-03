
## How to use

### URL()

```python
In [1]: from scrapper_tools import URL

In [2]: u = URL()

In [3]: u.validator('http://sample.om')
Out[3]: True

In [4]: u.validator('http://sample.')
Out[4]: False

In [5]: url = URL('http://www.example.com/sample?src=git&encode=jp')

In [6]: url.is_valid
Out[6]: True

In [7]: url.__dict__
Out[7]:
{'url': 'http://www.example.com/sample?src=git&encode=jp',
 'is_valid': True,
 'scheme': 'http',
 'netloc': 'www.example.com',
 'username': None,
 'password': None,
 'hostname': 'www.example.com',
 'port': None,
 'path': '/sample',
 'params': '',
 'query': 'src=git&encode=jp',
 'fragment': ''}

In [8]: url.query
Out[8]: 'src=git&encode=jp'

In [9]: url.get_query_val('src')
Out[9]: 'git'

In [10]: url.set_query_val('src', 'csv')
Out[10]: 'http://www.example.com/sample?src=csv&encode=jp'

In [11]: url
Out[11]: http://www.example.com/sample?src=git&encode=jp

In [12]: url.set_query_val('src', 'csv',update=True)
Out[12]: 'http://www.example.com/sample?src=csv&encode=jp'

In [13]: url
Out[13]: http://www.example.com/sample?src=csv&encode=jp

In [14]: url.get_root_address()
Out[14]: 'http://www.example.com'

In [15]: url.strip_query()
Out[15]: 'http://www.example.com/sample'

In [16]: url = URL('https://ja.wikipedia.org/wiki/日本語')

In [17]: url
Out[17]: https://ja.wikipedia.org/wiki/%E6%97%A5%E6%9C%AC%E8%AA%9E

In [18]: url.decode()
Out[18]: 'https://ja.wikipedia.org/wiki/日本語'

```

### Scrapper()

#### get_random_user_agent()

```python
n [1]: from scrapper_tools import Scrapper

In [2]: sc = Scrapper()

In [3]: sc.get_random_user_agent()
Out[3]: 'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36'

In [4]: sc.get_random_user_agent()
Out[4]: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/'

In [5]: sc.get_random_user_agent()
Out[5]: 'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36'

In [6]: sc.get_random_user_agent()
Out[6]: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'

In [7]: sc.get_random_user_agent()
Out[7]: 'Mozilla/5.0 (CrKey armv7l 1.5.16041) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.0 Safari/537.36'

In [8]: sc.get_random_user_agent()
Out[8]: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'

In [9]: sc.get_random_user_agent()
Out[9]: 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'

In [10]:
```


```python
In [2]: from scrapper_tools import URL, Scrapper, LogConfig
   ...:
   ...: logconfig = LogConfig()
   ...: logconfig.level = 'INFO'
   ...: sc = Scrapper(logconfig=logconfig.config())
   ...:
   ...: url = URL('https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unic
   ...: ode')
   ...: response = sc.request(url)
   ...:
   ...: content = response.content
   ...: print(f'code: {response.status_code}')
   ...:
code: 200

In [3]: from scrapper_tools import Scrapper, LogConfig
   ...:
   ...: logconfig = LogConfig()
   ...: logconfig.level = 'DEBUG'
   ...: sc = Scrapper(logconfig=logconfig.config())
   ...:
   ...: url = URL('https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unic
   ...: ode')
   ...: response = sc.request(url)
   ...:
   ...: content = response.content
   ...: print(f'code: {response.status_code}')
2022-06-02T19:34:31.885790+0900 LOG configure: {'handlers': [{'sink': <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>, 'level': 'DEBUG', 'format': '<green>{time}</green> <level>{message}</level>', 'colorize': True, 'serialize': False}]}
2022-06-02T19:34:31.886414+0900 URL: https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unicode
2022-06-02T14:34:32.092599+0900 response status_code: 200
code: 200

In [4]: logconfig
Out[4]: LogConfig(sink=None, level=DEBUG, format=<green>{time}</green> <level>{message}</level>, colorize=True, serialize=False

In [5]:
```
