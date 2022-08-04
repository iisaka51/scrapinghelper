from scrapinghelper import Scraper, ProxyManager, ProxyRotate

# tiny socks5 proxy
proxies = [ 'socks5://127.0.0.1:9050']
url = 'https://httpbin.org/ip'

scraper = Scraper(proxies=proxies)

# default proxy_rotate is ProxyRotate.NO_PROXY
# does not call render()
response = scraper.request(url, render=False)
print(response.html.text)

# using next proxy server.
response = scraper.request(url, proxy_rotate=ProxyRotate.NEXT, render=False)
print(response.html.text)

# using current proxy server.
response = scraper.request(url, proxy_rotate=ProxyRotate.KEEP, render=False)
print(response.html.text)

# using random proxy server.
response = scraper.request(url, proxy_rotate=ProxyRotate.RANDOM)
print(response.html.text)
