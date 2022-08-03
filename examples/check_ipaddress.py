from scrapinghelper import Scraper, ProxyManager, ProxyRotate

# tiny socks5 proxy
proxies = [ 'socks5://127.0.0.1:9050']
url = 'https://httpbin.org/ip'

scraper = Scraper(proxies=proxies)

response = scraper.request(url, render=False)
print(response.html.text)

response = scraper.request(url, proxy_rotate=ProxyRotate.NEXT, render=False)
print(response.html.text)

response = scraper.request(url, proxy_rotate=ProxyRotate.KEEP, render=False)
print(response.html.text)

# response = scraper.request(url, proxy_rotate=ProxyRotate.RANDOM)
response = scraper.request(url, proxy_rotate=ProxyRotate.KEEP)
print(response.html.text)
