from scrapinghelper import ProxyManager

p = ProxyManager()
print(p.proxies[:2])

print(p.next_proxy())
print(p.next_proxy())
print(p.get_random_proxy())

