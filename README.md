
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
