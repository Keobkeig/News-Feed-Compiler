print('starting run')
import news
print ('news done')
import BBC
print ('bbc done')
import apnews
print ('apnews done')
import reuters
print ('reuters done')
import theconversation
print('theconversation done')
import theguardian
print('theguardian done')
import CNN
print('CNN done')
import wikiNews
print('wikiNews done')
import re
import pandas as pd

csv_files = ['news_week.csv', 'theconversation.csv']

wiki_list = news.linkScraper()
print('list done')
for link in wiki_list:
    cnn = re.search(r'cnn.com', link)
    ap = re.search(r'apnews.com', link)
    bbc = re.search(r'bbc.com', link)
    gua = re.search(r'theguardian.com', link)
    reu = re.search(r'reuters.com', link)
    if cnn:
        CNN.cnnScraper(link)
    elif ap:
        apnews.scrap(link)
    elif bbc:
        BBC.bbcScraper(link)
    elif gua:
        theguardian.scrap(link)
    elif reu:
        reuters.scrap(link)

print('loop done')

csv_files.append('cnn.csv')
csv_files.append('bbc.csv')
csv_files.append('reuters.csv')
csv_files.append('theguardian.csv')
csv_files.append('apnews.csv')
 

df_csv_concat = pd.concat([pd.read_csv(file) for file in csv_files ], ignore_index=True)
df_csv_concat.to_csv('everything.csv', index=False)


