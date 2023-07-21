# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import datetime as dt
import re

# specify the url
urlpage = 'https://www.aljazeera.com/news' 
options = webdriver.FirefoxOptions()
options.add_argument('--headless')

#Retrieve URL 
driver = webdriver.Firefox(options)

#Get Date Time
today = dt.date.today()
week_ago = today - dt.timedelta(days=7)
#date_str = '13 Jul 2022'
#date_object = datetime.strptime(date_str, '%d %b %Y').date()

#Get articles that are 7 days ago
driver.get(urlpage)
#driver.execute_script("document.querySelector('#news-feed-container > button').click()")
count = 0
driver.implicitly_wait(60)
#driver.find_element(By.PARTIAL_LINK_TEXT, "")
while(True):
    if (len(driver.find_elements(By.XPATH, "//button[contains(@class,'show-more-button')]")) < 1):
        break
    else:
        #Sometimes Query Selector is Null
        driver.execute_script("document.querySelector('#news-feed-container > button').click()")
        #driver.find_element(By.XPATH, "//button[contains(@class,'show-more-button')]").click()
    #else:
    #    driver.execute_script("document.querySelector('#news-feed-container > button').click()")
    count+=1
    date = driver.find_elements(By.XPATH, ".//div[contains(@class,'date-simple')]/span[2]")[-1]
    if (week_ago > datetime.strptime(date.text, '%d %b %Y').date()):
        break
    if (count > 1):
        break
articles = driver.find_elements(By.TAG_NAME, "article")
#print("HEY", len(articles))

#Tags list 
url_list = []
for article in articles:
    link = article.find_element(By.XPATH, ".//a[contains(@class,'u-clickable-card__link')]").get_attribute("href")
    match = re.search(r'live', link)
    if not match:
        url_list.append(link)
    #title = article.find_element(By.TAG_NAME, "h3")
    #date = article.find_element(By.XPATH, ".//div[contains(@class,'date-simple')]/span[2]")
    #print(title.text)
    #print(date.text)
    #print(date.text)

print(len(url_list))
#Title, summary, full html content of article, picture links, video links, 
# categories, original date of publication, last updated date.

#publishedDate and lastDate are both meta tags

#Under a class called breadcrumbs
#Tags for categories are under a class called topics
#h1 tag for title
#main-content-area

#pictures = []
#videos = []
#figure = driver.find_elements(By.XPATH, './/main//figure')
df = pd.DataFrame(columns=["Title", "Summary", "HTML", "Pictures", "Videos", "Categories", "OG Date", "Update Date"])

for url in url_list:
    driver.get(url)
    driver.implicitly_wait(2)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')
    media_dict = dict()
    print(url)
    html_text = soup.find(id="main-content-area").find_all("p")
    #print(html_text)
    publishedDate = driver.find_element(By.NAME, "publishedDate").get_attribute("content")
    lastDate = driver.find_element(By.NAME, "lastDate").get_attribute("content")

    published_date_object = datetime.strptime(publishedDate[:10], '%Y-%m-%d').date()
    #print(published_date_object)
    last_date_object = datetime.strptime(lastDate[:10], '%Y-%m-%d').date()
    #print(publishedDate)
    #print(lastDate)
    category = driver.find_elements(By.XPATH, ".//div[contains(@class,'topics')]//a[2]")
    if (len(category) < 1):
        category = "No Category"
    else:
        category = driver.find_element(By.XPATH, ".//div[contains(@class,'topics')]//a[2]").text
    #print(category)

    title = driver.find_element(By.NAME, "pageTitle").get_attribute("content") #find_element(By.XPATH, ".//header[contains(@class, 'article-header')]/h1")
    summary = driver.find_element(By.NAME, "description").get_attribute("content")

    #print(title.text)
    #print(summary)

    pictures = []
    videos = []
    driver.implicitly_wait(10)
    figure = driver.find_elements(By.XPATH, './/main//figure')
    for fig in figure:
        if "iframe" in fig.get_attribute("innerHTML"):
            if (len(fig.find_elements(By.TAG_NAME, "iframe")) < 1):
                #videos.append(["N/A", "N/A"])
                continue
            src = fig.find_element(By.TAG_NAME, "iframe").get_attribute("src")
            figcaption = fig.find_element(By.TAG_NAME, "figcaption").text
            videos.append([src, figcaption])
        else:
            if (len(fig.find_elements(By.TAG_NAME, "img")) < 1):
                #pictures.append(["N/A", "N/A"])
                continue
            src = fig.find_element(By.TAG_NAME, "img").get_attribute("src")
            figcaption = fig.find_elements(By.TAG_NAME, "figcaption")
            if len(figcaption) == 0:
                pictures.append([src, 'No caption available'])
            else:
                pictures.append([src, figcaption[0].text])
    
    #print(pictures)
    #print(videos)

    new_row = {"Title": title, "Summary":summary, "HTML": html_text, "Pictures":pictures, 
               "Videos":videos, "Categories":category, "OG Date":publishedDate, "Update Date": lastDate}
    df.loc[len(df)] = [title, summary, html_text, pictures, videos, category, published_date_object, last_date_object]
    #print(url)
    #print(publishedDate, lastDate)

df.to_csv('news_week.csv', index=False, encoding='utf-8')
driver.quit()


