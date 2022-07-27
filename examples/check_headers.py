import scraper_tools as sct
from pprint import pprint

scraper = sct.Scraper()
response = scraper.request('http://httpbin.org/headers')
pprint(response.json())
