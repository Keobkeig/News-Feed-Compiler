from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
import pandas as pd

def cnnScraper(link):
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

    try:
        pubdate = driver.find_element(By.XPATH, "//meta[@property= 'article:published_time']").get_attribute('content')[:10]
        lastmod = driver.find_element(By.XPATH, "//meta[@property= 'article:modified_time']").get_attribute('content')[:10]
        
    except:
        pubdate = driver.find_element(By.XPATH, "//meta[@name= 'pubdate']").get_attribute('content')[:10]
        lastmod = driver.find_element(By.XPATH, "//meta[@name= 'lastmod']").get_attribute('content')[:10]
    
    datepub = datetime.strptime(pubdate, '%Y-%m-%d').date()
    datemod = datetime.strptime(lastmod, '%Y-%m-%d').date()

    images = []
    figures = driver.find_elements(By.TAG_NAME, 'figure')
    
    for figure in figures:
        src = figure.find_element(By.TAG_NAME, 'img').get_attribute('src')
        cap = figure.text
        images.append({'src': src, 'caption': cap})

    pictures = driver.find_elements(By.TAG_NAME, 'picture')
    for picture in pictures:
        src = picture.find_element(By.TAG_NAME, 'img').get_attribute('src')
        cap = picture.find_element(By.TAG_NAME, 'img').get_attribute('alt')
        images.append({'src': src, 'caption': cap})
    
    videoss = []
    videos = driver.find_elements(By.XPATH, "//div[@data-component-name= 'video-resource']")
    for video in videos:
        src = video.find_element(By.TAG_NAME, 'video').get_attribute('poster')
        cap = video.find_element(By.CLASS_NAME, 'video-resource__headline').text
        videoss.append({'src': src, 'caption': cap})    
    
    categories = driver.find_element(By.XPATH, "//meta[@name= 'keywords']").get_attribute('content')

    df.loc[len(df)] = [title, summary, html, images, videoss, categories, datepub, datemod]
    df.to_csv("cnn.csv", index=False)
    driver.quit()


