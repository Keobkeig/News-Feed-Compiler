import re
import pandas as pd
from datetime import date, timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

url = "https://theconversation.com/us"
 
options = Options() 
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--log-level=3")

driver = webdriver.Firefox(options)
driver.get(url)

wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "more")))

more_button = driver.find_element(By.CLASS_NAME ,"more").find_element(By.TAG_NAME, "a").click()

# print("Page is ready!")

today = date.today()
week_ago = today - timedelta(days=7)

wait = WebDriverWait(driver, 10)
wait.until(EC.visibility_of_element_located((By.TAG_NAME, "article")))

links = []

df = pd.DataFrame(columns=["Title", "Summary", "HTML", "Pictures", "Videos", "Categories", "OG Date", "Update Date"])

def scrap(driver, link):
    driver.get(link)
    
    title = driver.find_element(By.TAG_NAME, "h1").text
    summary = driver.find_element(By.XPATH, "/html/head/meta[7]").get_attribute("content").strip()

    html = driver.find_element(By.TAG_NAME, "article").get_attribute("innerHTML")

    pictures = []
    videos = []
        
    figure = driver.find_elements(By.XPATH, '//figure')
       
    for fig in figure:
        if "iframe" in fig.get_attribute("innerHTML"):
            src = fig.find_element(By.TAG_NAME, "iframe").get_attribute("src")
            figcaption_element = fig.find_elements(By.TAG_NAME, "figcaption")
            figcaption = figcaption_element[0].text if figcaption_element else ""
            videos.append([src, figcaption])
        else:
            src = fig.find_element(By.TAG_NAME, "img").get_attribute("src")
            figcaption = fig.find_element(By.TAG_NAME, "figcaption").text
            pictures.append([src, figcaption])
        
    categories_list = []
    categories = driver.find_elements(By.CLASS_NAME, "topic-list-item")
    for category in categories:
        categories_list.append(category.text)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    original_date = soup.find("meta", {"name":"pubdate"})["content"]
    original_date = datetime.strptime(original_date, "%Y%m%d").date()

    updated_date = soup.find("meta", {"property":"og:updated_time"})["content"]
    updated_date = datetime.strptime(updated_date, "%Y-%m-%dT%H:%M:%S%z").date()
        
    df.loc[link] = [title, summary, html, pictures, videos, categories_list, original_date, updated_date]

def get_articles(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.visibility_of_element_located((By.TAG_NAME, "article")))
    articles = driver.find_elements(By.TAG_NAME, "article")

    for article in articles:
        link = article.find_element(By.CLASS_NAME, "article-link").get_attribute("href")
        original_date = article.find_element(By.TAG_NAME, "img").get_attribute("data-src")
        original_date = re.search(r"file-(\d+)-", original_date).group(1) 
        original_date = datetime.strptime(original_date, "%Y%m%d").date()

        if original_date >= week_ago:
            links.append(link)

def go_next(driver):
    next_button = driver.find_element(By.CLASS_NAME, "next").find_element(By.TAG_NAME, "a")
    next_url = next_button.get_attribute("href")
    driver.get(next_url)

# Get the articles from the first, second, and third page only
get_articles(driver)
go_next(driver)
get_articles(driver)
go_next(driver)
get_articles(driver)

for link in links:
    scrap(driver, link)

driver.quit()

df.to_csv("theconversation.csv", index=False)
