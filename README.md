
## How to use

### URL()

```python
In [2]: from web_scrapper import URL, Scrapper, LogConfig
   ...:
   ...: url = URL('https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unic
   ...: ode')

In [3]: url
Out[3]: https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unicode

In [4]: url.is_valid
Out[4]: True

In [5]: url.__dict__
Out[5]:
{'url': 'https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unicode',
 'is_valid': True,
 'scheme': 'https',
 'netloc': 'www.houjin-bangou.nta.go.jp',
 'path': '/download/zenken/',
 'params': '',
 'query': '',
 'fragment': 'csv-unicode'}

In [6]:
```

### Scrapper()

#### get_random_user_agent()

```python
n [1]: from web_scrapper import Scrapper

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
In [2]: from web_scrapper import URL, Scrapper, LogConfig
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

In [3]: from web_scrapper import URL, Scrapper, LogConfig
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
2022-06-02T14:34:31.885790+0900 LOG configure: {'handlers': [{'sink': <_io.TextIOWrapper name='<stdout>' mode='w' encoding='utf-8'>, 'level': 'DEBUG', 'format': '<green>{time}</green> <level>{message}</level>', 'colorize': True, 'serialize': False}]}
2022-06-02T14:34:31.886414+0900 URL: https://www.houjin-bangou.nta.go.jp/download/zenken/#csv-unicode
2022-06-02T14:34:32.092599+0900 response status_code: 200
code: 200

In [4]: logconfig
Out[4]: LogConfig(sink=None, level=DEBUG, format=<green>{time}</green> <level>{message}</level>, colorize=True, serialize=False

In [5]:
```
