import re
import pandas as pd
from datetime import date, timedelta, datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from bs4 import BeautifulSoup

urls = [
    "https://www.theguardian.com/sport/2023/jul/02/mcc-unreservedly-apologised-to-australia-after-long-room-incident-england-ashes",
    "https://www.theguardian.com/world/2023/jul/04/russia-ukraine-war-at-a-glance-what-we-know-on-day-496-of-the-invasion",
    "https://www.theguardian.com/world/2023/jul/11/senior-russian-draft-officer-shot-dead-while-running-in-park",
]

# today = date.today()
# week_ago = today - timedelta(days=7)

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

    og_date = soup.find("meta", {"property": "article:published_time"})["content"]
    og_date = datetime.strptime(og_date, "%Y-%m-%dT%H:%M:%S.%fZ").date()

    # if og_date < week_ago:
    #     return
  
    title = soup.find("h1").text
  
    summary = soup.find("meta", {"name": "description"})["content"].strip()
    
    html = soup.find("article")

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
                #find img with regex
                if "srcset" in fig.get_attribute("innerHTML"):
                    src = re.search('srcset="([^"]+)"', fig.get_attribute("innerHTML")).group(1)

                    #if there is multiple images, get the first one
                    if "," in src:
                        src = src.split(",")[0].strip()
                
                figcaption_element = fig.find_elements(By.TAG_NAME, "figcaption")

                if not figcaption_element:    
                    try:
                        figcaption = re.search('dcr-1y4fm6e">([^<]+)<', fig.get_attribute("innerHTML")).group(1)
                    except:
                        figcaption = ""
                else:
                    figcaption = figcaption_element[0].text

                pictures.append([src, figcaption])

    categories = []
    for category in soup.find_all("a", {"class": "dcr-ln1l5t"}):
        categories.append(category.text)
   
    update_date = soup.find("meta", {"property": "article:modified_time"})["content"]
    update_date = datetime.strptime(update_date, "%Y-%m-%dT%H:%M:%S.%fZ").date()
    
    
    df.loc[len(df)] = [title, summary, html, pictures, videos, categories, og_date, update_date]
    df.to_csv("theguardian.csv", index=False)
    driver.quit()

"""
testing on links    
scrap(driver, urls[0])
scrap(driver, urls[1])
scrap(driver, urls[2])

print(df)
"""

