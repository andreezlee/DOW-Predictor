# Training Examples Setup

import os
import MySQLdb
import json

def create_news_examples():
    # Assume already scraped all articles into SQL database
    all_articles=dict()
    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()

    # Retrieve all articles for each date
    cursor.execute("SELECT article_date, article_url, full_text FROM all_articles")
    for row in cursor.fetchall():
        article_date = row[0]
        article_url = row[1]
        full_text = row[2]

        dict_entry = (article_url, len(full_text))
        if article_date not in all_articles:
            all_articles[article_date]=[dict_entry]
        else:
            all_articles[article_date].append(dict_entry)

    # For each date retrieved, grab the up to 3 longest articles
    # Add data to database
    insert_query="INSERT INTO data_examples (article_date, {}) VALUES (%s, {})"
    for day in all_articles.keys():
        all_articles[day].sort(reverse=True, key=lambda x: x[1])
        longest=all_articles[day]
        if len(longest) == 1:
            query=insert_query.format("article1", "%s")
            query_data=(day, longest[0][0])
        elif len(longest) == 2:
            query=insert_query.format("article1, article2", "%s, %s")
            query_data=(day, longest[0][0], longest[1][0])
        else:
            query=insert_query.format("article1, article2, article3", "%s, %s, %s")
            query_data=(day, longest[0][0], longest[1][0], longest[2][0])
        cursor.execute(query, query_data)

    sql_cxn.commit()
    sql_cxn.close()

if __name__ == "__main__":
    create_news_examples()