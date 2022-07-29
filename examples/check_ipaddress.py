from scrapinghelper import Scraper, URL

# tiny socks5 proxy
proxies = {
        'http':'socks5:/127.0.0.1:9050',
        'https':'socks5://127.0.0.1:9050'
        }
url = 'https://httpbin.org/ip'

scraper = Scraper()
response = scraper.request(url)
print(response.html.text)
response = scraper.request(url,proxies=proxies)
print(response.html.text)
response = scraper.request(url,proxies=proxies, render=False)
print(response.html.text)
