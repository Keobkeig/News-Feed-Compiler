import re
import pandas as pd
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By

urls = [
    "https://apnews.com/article/east-timor-prime-minister-gusmao-9d3f254834da006a71e1597f361a33a5",
    "https://apnews.com/article/deaths-toxic-gas-leak-south-africa-a69a73e5c454fdfd7331be873556eab9",
    "https://apnews.com/article/china-heat-weather-flood-7a2ef4f89ebbf63cd8158f1954c78633"
]

today = date.today()
week_ago = today - timedelta(days=7)

def scrap(link):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--log-level=3")

    driver = webdriver.Firefox(options)

    df = pd.DataFrame(columns=["Title", "Summary", "HTML", "Pictures", "Videos", "Categories", "OG Date", "Update Date"])

    driver.get(link)
    driver.implicitly_wait(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    og_date = soup.find("meta", {"property": "article:published_time"})["content"] if soup.find("meta", {"property": "article:published_time"}) else ""
    og_date = re.sub(r"T.*", "", og_date).strip()
    
    og_date = datetime.strptime(og_date, "%Y-%m-%d").date()

    # if og_date < week_ago:
    #     return

    title = soup.find("h1").text
    summary = soup.find("meta", {"name": "description"})["content"].strip()
    html = soup.find("main", {"class": "Page-main"})
    
    pictures = []
    videos = []

    figures = driver.find_elements(By.XPATH, '//figure')

    for fig in figures:
        # if there is a slideshow of images
        if fig.find_elements(By.CLASS_NAME, "Carousel") != []:
            for img in fig.find_elements(By.CLASS_NAME, "CarouselSlide"):
                src = img.find_element(By.TAG_NAME, "img").get_attribute("src")
                figcaption = img.find_element(By.CLASS_NAME, "CarouselSlide-infoDescription").text
                pictures.append([src, figcaption])
        # if there is a single image
        else:
            if fig.find_element(By.TAG_NAME, "img").get_attribute("src") == None:
                src = re.search('srcset="([^"]+)"', fig.get_attribute("innerHTML")).group(1)

                #if there is multiple images, get the first one
                if "," in src:
                    src = src.split(",")[0]
            else:
                src = fig.find_element(By.TAG_NAME, "img").get_attribute("src")
            
            figcaption_element = fig.find_elements(By.TAG_NAME, "figcaption")
            figcaption = figcaption_element[0].text if figcaption_element else fig.find_element(By.CLASS_NAME, "dcr-12evv1c").text
            pictures.append([src, figcaption])
        
    categories = []
    for category in soup.find_all("meta", {"property": "article:tag"}):
        categories.append(category["content"])

    update_date = soup.find("meta", {"property": "article:modified_time"})["content"]
    update_date = re.sub(r"T.*", "", update_date).strip()
    update_date = datetime.strptime(update_date, "%Y-%m-%d").date()
    # print(update_date)
    
    df.loc[len(df)] = [title, summary, html, pictures, videos, categories, og_date, update_date]
    df.to_csv("apnews.csv", index=False)
    driver.quit()

"""
for url in urls:
    scrap(driver, url)
print(df)
"""

