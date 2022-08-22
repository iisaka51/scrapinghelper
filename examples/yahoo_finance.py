from typing import Any
import numpy as np
from scrapinghelper import Scraper, URL

MARKET_SUMMARY = (
    '#market-summary > div > div.D\(ib\).Fl\(start\).W\(100\%\) '
    '> div.Carousel-Mask.Pos\(r\).Ov\(h\).market-summary'
    '.M\(0\).Pos\(r\).Ov\(h\).D\(ib\).Va\(t\) > ul'
)

class YHFinance(Scraper):
    Finance = URL('https://finance.yahoo.com/')

    def __init__(self, **kwargs: Any):
        super().__init__(browser_args='--incognito', **kwargs)
        self.response = self.request(self.Finance.url)

    def get_market_summary(self)->list:
        contents = self.get_texts(MARKET_SUMMARY)
        return contents

if __name__ == '__main__':
    from scrapinghelper.utils import split_list

    yahoo = YHFinance()
    summary = yahoo.get_market_summary()[0]
    for data in split_list(summary, 5):
        print(data)
