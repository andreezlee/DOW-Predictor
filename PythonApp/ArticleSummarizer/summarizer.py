import ArticleSummarizer.setup as setup
import pickle
import math
from nltk.tokenize import word_tokenize, sent_tokenize

# Generate scores for words based on how common they are (minus stop words)
def word_scores(article):
    article=setup.get_around_bug(article)
    all_sentences=sent_tokenize(article)
    all_words=list()
    for sen in all_sentences:
        sen=setup.get_around_bug(sen)
        all_words+=word_tokenize(sen)
    word_counts=dict()

    with open('stop_words.pickle', 'rb') as f:
        stop_words=pickle.load(f)
        for w in all_words:
            if w not in stop_words:
                if w not in word_counts:
                    word_counts[w]=1
                else:
                    word_counts[w]+=1
    word_rankings=list(word_counts.items())
    word_rankings.sort(reverse=True, key=lambda x: x[1])
    scores=dict()
    for i in range(len(word_rankings)):
        scores[word_rankings[i][0]]=i
    return scores



def summarize(article):
    article=setup.preprocess_article(article)
    scores=word_scores(article)
    with open('stop_words.pickle', 'rb') as f:
        stop_words=pickle.load(f)

    # Tokenize into sentences
    article=setup.get_around_bug(article)
    all_sentences=sent_tokenize(article)

    # Generate score for each sentence
    sen_scores=dict()
    for key_sen in all_sentences:
        sen=setup.get_around_bug(key_sen)
        all_words=word_tokenize(sen)

        sen_score=0
        for w in all_words:
            if w not in stop_words:
                sen_score+=scores[w]
        sen_scores[key_sen]=sen_score/max(len(all_words),1)

    sen_rankings=list(sen_scores.items())
    sen_rankings.sort(key=lambda x: x[1])

    # Create summary
    best_sentences=set()
    for i in range(min(5, math.ceil(len(all_sentences)/2))):
        best_sentences.add(sen_rankings[i][0])

    summary=""
    for sen in all_sentences:
        if sen in best_sentences:
            summary += " " + sen

    return summary

# Test script
if __name__ == "__main__":
    import MySQLdb

    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()

    cursor.execute("SELECT full_text FROM all_articles LIMIT 10")
    for row in cursor.fetchall():
        article=row[0]
        print("FULL ARTICLE: \n" + article)
        print("ARTICLE SUMMARY: \n" + summarize(article))

    cursor.close()
    sql_cxn.close()
