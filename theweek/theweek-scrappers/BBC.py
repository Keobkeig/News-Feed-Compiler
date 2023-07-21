from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import json
import pandas as pd


def bbcScraper(link):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options)

    df = pd.DataFrame(columns=["Title", "Summary", "HTML", "Pictures", "Videos", "Categories", "OG Date", "Update Date"])

    driver.get(link)
    driver.implicitly_wait(3)
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    title = soup.title.string
    summary = driver.find_element(By.XPATH, "//meta[@name= 'description']").get_attribute('content')
    html = soup.article.prettify()

    figures = driver.find_elements(By.TAG_NAME, 'figure')
    images = []
    videos = []
    for figure in figures:
        try:
            src = figure.find_element(By.TAG_NAME, 'iframe').get_attribute('src')
            try:
                figcap = figure.find_element(By.TAG_NAME, 'figcaption')
                cap = figcap.find_element(By.TAG_NAME, 'div').text
                videos.append({'src': src, 'cap': cap})
            except:
                videos.append({'src': src, 'cap': ''})
        except:
            src = figure.find_element(By.TAG_NAME, 'img').get_attribute('src')
            try:
                figcap = figure.find_element(By.TAG_NAME, 'figcaption')
                cap = figcap.find_element(By.TAG_NAME, 'div').text
                images.append({'src': src, 'cap': cap})
            except:
                images.append({'src': src, 'cap': ''})

    try:
        categories = driver.find_element(By.XPATH, "//meta[@property= 'article:section']").get_attribute('content')
    except:
        categories = ''
    jsondates = driver.find_element(By.XPATH, "//script[@type= 'application/ld+json']").get_attribute('innerHTML')
    dates = json.loads(jsondates)
    pub = dates['datePublished'][:10]
    mod = dates['dateModified'][:10]

    datepub = datetime.strptime(pub, '%Y-%m-%d').date()
    datemod = datetime.strptime(mod, '%Y-%m-%d').date()

    df.loc[len(df)] = [title, summary, html, images, videos, categories, datepub, datemod]
    df.to_csv("bbc.csv", index=False)
    driver.quit()
