import pandas as pd
from scrapinghelper import Scraper, URL

url = 'https://www.socks-proxy.net/'

scraper = Scraper()
response = scraper.request(url)
# proxy_list = [ x.text.split('\n')
#      for x in response.html.find('table')[0].find('tr') ]
proxy_list = scraper.get_texts(response.html)
df = pd.DataFrame(proxy_list[1:], columns=proxy_list[0])
# df.to_csv('socks_proxy_list.csv')
df.head()
df.info()

