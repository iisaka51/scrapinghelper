import scrapinghelper as sch
from pprint import pprint

scraper = sch.Scraper()
response = scraper.request('http://httpbin.org/headers')
pprint(response.json())
