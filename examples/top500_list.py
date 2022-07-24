import pandas as pd
from scraper_tools import Scraper, URL

url = 'https://www.top500.org/lists/top500/2022/06/'

scraper = Scraper()
response = scraper.request(url)
top500  = [ x.text.split('\n')
            for x in response.html.find('table')[0].find('tr') ]
top500[0] = ['Rank', 'System', 'Onwer', 'Country',
             'Cores', 'Rmax (PFlop/s)', 'Rpeak (PFlop/s)', 'Power (kW)']

df = pd.DataFrame(top500[1:], columns=top500[0])
df.set_index('Rank', inplace=True)
# df.to_csv('top500_list.csv')

