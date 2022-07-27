import pandas as pd
import scrapinghelper as sch

logconfig = sch.LogConfig()
scraper = sch.Scraper(logconfig=logconfig)
response  = scraper.request(URL)

df = pd.read_csv('indicators.csv')

for n in range(len(df)):
    filename = df.iloc[n]['filename']
    link = df.iloc[n]['link']
    scraper.download_file(link, filename, sleep=6, user_agent='random')
