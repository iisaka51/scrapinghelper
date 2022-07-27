from scrapinghelper import Scraper
from pprint import pprint

scraper = Scraper()
response = scraper.request('http://httpbin.org/headers')
pprint(response.json())
