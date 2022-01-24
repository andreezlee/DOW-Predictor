import csv
from ArticleSummarizer.summarizer import summarize
import MySQLdb

def create_training_data_csv():
    # Dictionaries to organize information
    article_references=dict()
    article_summaries=dict()
    dji_info=dict()

    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()

    # Pull all data from database
    cursor.execute('SELECT * FROM data_examples')
    for row in cursor.fetchall():
        date_key=row[0]
        article_references[date_key]=[row[1],row[2],row[3]]

    cursor.execute('SELECT article_url, full_text FROM all_articles')
    for row in cursor.fetchall():
        url_key=row[0]
        full_text=row[1]
        article_summaries[url_key]=summarize(full_text)

    cursor.execute('SELECT sample_date, percent_change, estimate FROM dji_data')
    for row in cursor.fetchall():
        date_key=row[0]
        percent_change=row[1]
        est=row[2]
        dji_info[date_key]=(percent_change, est)

    cursor.close()
    sql_cxn.close()

    # Generate CSV file with the organized data
    with open('training_data.csv', 'w') as csv_file:
        fieldnames = ['date', 'article1', 'article2', 'article3', 'dow jones', 'estimate']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for key in article_references:
            date_field=key
            if article_references[key][0] in article_summaries:
                article1_field=article_summaries[article_references[key][0]]
            else:
                article1_field=''
            if article_references[key][1] in article_summaries:
                article2_field=article_summaries[article_references[key][1]]
            else:
                article2_field=''
            if article_references[key][2] in article_summaries:
                article3_field=article_summaries[article_references[key][2]]
            else:
                article3_field=''
            dow_jones_field, estimate_field=dji_info[key]
            writer.writerow(
                {
                'date': date_field, 'article1' : article1_field,
                'article2': article2_field, 'article3': article3_field,
                'dow jones': dow_jones_field, 'estimate': estimate_field == b'\x01'
                })

import pickle

def create_model_data():
    word_counts=dict()
    word_array=list()
    word_index=dict()

    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()

    # Pull all data from database
    cursor.execute('SELECT * FROM data_examples')
    for row in cursor.fetchall():
        date_key=row[0]
        article_references[date_key]=[row[1],row[2],row[3]]

    cursor.execute('SELECT article_url, full_text FROM all_articles')
    for row in cursor.fetchall():
        url_key=row[0]
        full_text=row[1]
        article_summaries[url_key]=summarize(full_text)

if __name__ == "__main__":
    create_training_data_csv()