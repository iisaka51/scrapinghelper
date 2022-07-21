import pandas as pd
from requests_html import HTMLSession
import scraper_tools as sct

_BASE_URL='https://www.forexpnf.info/forex-indicators'
_DOWNLOAD_URL = (
    f'{_BASE_URL}/free-forex-indicators-a-j/'
    'free-forex-indicators-a-j/'
)
_OBJECT_SELECTOR=(
    '#page > div > div > div > section > div:nth-child(2) > article'
    ' > div > table:nth-child(5) > tbody'
)

logconfig = sct.LogConfig()
logconfig.level = 'INFO'

scraper = sct.Scraper(logconfig=logconfig)
response  = scraper.request(_DOWNLOAD_URL)

files = list()
for atag in s.get_links(response.html, endswith=['.mq4', '.mq5']):
    if atag.link:
        if atag.text:
            filename = atag.text
        else:
            filename=atag.link.basename
        files.append(dict( filename=filename, link=atag.link))

df = pd.DataFrame(files)
if len(df) >0:
    pattern = "|".join([' ', '/', '\(', '\)', '\[', '\]'])
    df['filename'] = df['filename'].str.replace('&', '_and_')
    df['filename'] = df['filename'].str.replace(pattern, '_')

for n in range(len(df)):
    filename = df.iloc[n]['filename']
    link = df.iloc[n]['link']
    scraper.download_file(link, filename, sleep=30, user_agent='random')
