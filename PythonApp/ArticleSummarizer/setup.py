import pickle
from nltk.tokenize import word_tokenize, sent_tokenize
import MySQLdb
import re

# Add space between sentences for sentence tokenizer
def preprocess_article(article):
    return re.sub(r'([a-z])\.([A-Z])', r'\1. \2', article)

# Get around NLTK tokenize bug
def get_around_bug(s):
    while len(s) > 0 and not s[0].isalnum():
        if len(s) == 1:
            return ""
        s = s[1:]
    return s

# Find common words to exclude from future tasks
def create_stop_words():
    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()
    article_counts = dict()

    # Retrieve all articles for each date
    cursor.execute("SELECT full_text FROM all_articles")
    all_articles=cursor.fetchall()
    num_articles=len(all_articles)
    print("Obtained {} articles".format(num_articles))
    for row in all_articles:
        word_counts = dict()
        full_text = row[0]

        # Tokenization for word counts
        full_text = preprocess_article(full_text)
        full_text = get_around_bug(full_text)
        all_sentences = sent_tokenize(full_text)
        for sen in all_sentences:

            sen = get_around_bug(sen)
            all_tokens = word_tokenize(sen)
            for t in all_tokens:
                if t in word_counts:
                    word_counts[t] += 1
                else:
                    word_counts[t] = 1

        counts_list = list(word_counts.items())
        counts_list.sort(reverse=True, key=lambda x: x[1])

        # Add top fifteen most popular terms to article counts
        index = 0
        for c in counts_list:
            if c[0] in article_counts:
                article_counts[c[0]] += 1
            else:
                article_counts[c[0]] = 1
            index += 1
            if index >= 15:
                break

    # Develop stop words set based on 10% of all articles
    stop_words=set()
    for w in article_counts.keys():
        if article_counts[w] > num_articles/10:
            print("Found stop word: " + w)
            stop_words.add(w)

    with open('stop_words.pickle', 'wb') as f:
        pickle.dump(stop_words, f)

    cursor.close()
    sql_cxn.close()

if __name__ == "__main__":
    create_stop_words()