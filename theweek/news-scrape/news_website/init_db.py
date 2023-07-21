import sqlite3
import csv
import sys

maxInt = sys.maxsize

while True:
    try:
        csv.field_size_limit(maxInt)
        break
    except OverflowError:
        maxInt = int(maxInt/10)

con = sqlite3.connect("news_websites.db")    
cur = con.cursor()
cur.execute("CREATE TABLE t (Title, Summary ,HTML, Pictures, Videos, Categories, OG_Date, Update_Date);") # use your column names here

with open('everything.csv','r', encoding='utf8')  as fin: # `with` statement available in 2.5+
    # csv.DictReader uses first line in file for column headings by default
    dr = csv.DictReader(fin) # comma is default delimiter
    to_db = [(i['Title'], i['Summary'], i['HTML'], i['Pictures'], i['Videos'], i['Categories'], i['OG Date'], i['Update Date']) for i in dr]

cur.executemany("INSERT INTO t (Title, Summary ,HTML, Pictures, Videos, Categories, OG_Date, Update_Date) VALUES (?, ?, ?, ?, ?, ?, ?, ?);", to_db)
con.commit()
con.close()