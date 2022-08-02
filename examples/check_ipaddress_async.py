import asyncio
from scrapinghelper import Scraper, URL

# tiny socks5 proxy
proxies = {
        'http':'socks5:/127.0.0.1:9050',
        'https':'socks5://127.0.0.1:9050'
        }
url = 'https://httpbin.org/ip'

scraper = Scraper()
async def check_ipaddress():
    response = await scraper.request_async(url,proxies=proxies)
    print(response.html.text)

loop = asyncio.get_event_loop()

# you have another event loop. i.e.: run this script from  pysider.
if loop.is_running:
    import nest_asyncio
    nest_asyncio.apply()

feature = asyncio.ensure_future(check_ipaddress())
loop.run_until_complete(feature)

