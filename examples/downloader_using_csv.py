import pandas as pd
from scrapinghelper import Scraper, LogConfig

logconfig = LogConfig()
scraper = Scraper(logconfig=logconfig)

df = pd.read_csv('indicators.csv')

for n in range(len(df)):
    filename = df.iloc[n]['filename']
    link = df.iloc[n]['link']
    scraper.download_file(link, filename, sleep=6, user_agent='random')
