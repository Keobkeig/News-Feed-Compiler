from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime, timedelta
import re

urlpage = 'https://en.wikipedia.org/wiki/Portal:Current_events/July_2023'

options = Options()
options.headless = True
driver = webdriver.Firefox(options)

driver.get(urlpage)
driver.implicitly_wait(2)

events = driver.find_elements(By.XPATH, "//div[@class= 'current-events-main vevent']")

lastweek = (datetime.today() - timedelta(weeks = 1)).strftime("%B %d, %Y")


def weekScraper(startdate, events):
    for event in events:
        match = re.search(startdate, event.find_element(By.CLASS_NAME, 'summary').text)
        if match:
            theweek = events[events.index(event): events.index(event) + 8]
    
    return theweek

week = weekScraper(lastweek, events)

def linkScraper():
    links = []
    for day in week:
        id = day.get_attribute('id')
        xpath = "//div[@id= '" + id + "']//a[@rel= 'nofollow'][@class= 'external text']"
        hrefs = day.find_elements(By.XPATH, xpath)
        for href in hrefs:
            link = href.get_attribute('href')
            match = (re.search(r'cnn.com', link) or re.search(r'reuters.com', link) or re.search(r'bbc.com/news/', link) or
                     re.search(r'apnews.com', link) or re.search(r'theguardian.com', link))
            if match:
                links.append(link)
    driver.quit()
    return links



