# import libraries
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
from datetime import datetime
import datetime as dt

# specify the url
# urlpage = 'https://www.reuters.com/world/wmo-warns-risk-heart-attacks-deaths-heatwave-intensifies-2023-07-18/'

#Get Date Time
# today = dt.date.today()
# week_ago = today - dt.timedelta(days=7)
#date_str = '13 Jul 2022'
#date_object = datetime.strptime(date_str, '%d %b %Y').date()


def scrap(link):
    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    driver = webdriver.Firefox(options)
    # #Get articles that are 7 days ago
    # driver.get(urlpage)
    # #driver.execute_script("document.querySelector('#news-feed-container > button').click()")
    # count = 0
    # driver.implicitly_wait(60)

    df = pd.DataFrame(columns=["Title", "Summary", "HTML", "Pictures", "Videos", "Categories", "OG Date", "Update Date"])

    driver.get(link)
    driver.implicitly_wait(3)
    #page_source = driver.page_source
    #soup = BeautifulSoup(page_source, 'html.parser')
    #html_text = soup.find(id="main-content-area").find_all("p")
    # print(urlpage)

    #HTML_Text
    paragraphs = driver.find_elements(By.XPATH, ".//div[contains(@class,'article-body')]//p")
    html_text = ""
    for p in paragraphs:
        html_text += p.text
    #print(html_text)

    publishedDate = driver.find_element(By.NAME, "article:published_time").get_attribute("content")
    lastDate = driver.find_element(By.NAME, "article:modified_time").get_attribute("content")
    published_date_object = datetime.strptime(publishedDate[:10], '%Y-%m-%d').date()
    last_date_object = datetime.strptime(lastDate[:10], '%Y-%m-%d').date()

    category = driver.find_element(By.XPATH, ".//span[@data-testid='Heading']//a").text
    #print(category.text)

    title = driver.find_element(By.TAG_NAME, "h1").text
    #print(title.text)

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
            figcaption = fig.find_element(By.TAG_NAME, "figcaption").text
            pictures.append([src, figcaption])

    # print(pictures)
    # print(videos)
    summary = driver.find_element(By.NAME, "description").get_attribute("content")


    df.loc[len(df)] = [title, summary, html_text, pictures, videos, category, published_date_object, last_date_object]
    df.to_csv('reuters.csv', index=False, encoding='utf-8')
    driver.quit()



