# importing flask
from flask import Flask, render_template
import csv  
# importing pandas module
import pandas as pd
import sqlite3
from tabulate import tabulate
from collections import defaultdict

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('news_websites.db')
    conn.row_factory = sqlite3.Row
    return conn
    
def get_tag_counts():
    tag_counts = defaultdict(int)
    conn = get_db_connection()
    cur = conn.cursor()  
    cur.execute("SELECT categories FROM t")

    tag_counts = defaultdict(int)
    rows = cur.fetchall()

    for row in rows:
        tags = row[0].split(',')
    for tag in tags:
        tag_counts[tag] += 1

    conn.close()

    return tag_counts    
   
# route to html page - "table"
@app.route('/')
@app.route('/table')
def table():
    conn = get_db_connection()
    res = conn.execute("SELECT Title, Summary FROM t").fetchall()
    conn.close()
    df = pd.read_csv('everything.csv')[['Title', 'Summary']]
    #print(data)
    #for d in data:
        #print('hello')
        #print(d)
    #print(df.values.tolist())
    tag_counts = get_tag_counts()
  
    popular_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    return render_template("news_web.html", column_names=['Title', 'Summary'], row_data=res,
                           link_column="ID", zip=zip, popular_tags=popular_tags)
    #return render_template('news_web.html', tables=[data], titles=[''])

@app.route('/news/<int:news_id>')
def find_info(news_id):
    
    # converting csv to html
    conn = get_db_connection()
    res = conn.execute("SELECT Categories, Pictures, Videos, HTML, OG_Date, Update_Date FROM t").fetchall()
    #or rows in res:
    #    print(rows[0])
    conn.close()
    #data = pd.read_csv('news_week.csv')[['Categories', "Pictures", 
    #                "Videos", "HTML", "OG Date", "Update Date"]].iloc[news_id].to_frame()
    #print(type(data))
    #print(df)
    #print(data.to_html())
    #print('break')
    row = [res[news_id][0], res[news_id][1], res[news_id][2], res[news_id][3], res[news_id][4], res[news_id][5]]
    df = pd.DataFrame(row).transpose()
    df.columns=['Categories', "Pictures", 
                    "Videos", "HTML", "OG Date", "Update Date"]
    #print(tabulate(row, tablefmt='html'))
    return render_template('news_summary.html', tables=[df.to_html(index=False)], titles=[''])  
  
if __name__ == "__main__":
    app.run(host="localhost", port=int("5000"))