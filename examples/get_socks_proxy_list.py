import pandas as pd
from scraper_tools import Scraper, URL

url = 'https://www.socks-proxy.net/'

scraper = Scraper()
response = scraper.request(url)
proxy_list = [ x.text.split('\n')
               for x in response.html.find('table')[0].find('tr') ]
df = pd.DataFrame(proxy_list[1:], columns=proxy_list[0])
df.to_csv('socks_proxy_list.csv')

