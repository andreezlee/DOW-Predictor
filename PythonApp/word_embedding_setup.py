import numpy as np
import pickle
import csv
import MySQLdb
from os.path import exists
from nltk.tokenize import word_tokenize, sent_tokenize
from ArticleSummarizer.setup import preprocess_article, get_around_bug

# Defining constants
max_vocab=30000 # Max number of words in system
window_size=5 # Building co-occurrence from window


# Returns all text at the "document" (i.e. sentence) level
def obtain_all_sentences():
    sql_cxn = MySQLdb.connect('localhost','root','gwailo98(*','predictor')
    cursor = sql_cxn.cursor()

    all_text=""

    # Pull all data from database
    cursor.execute('SELECT article_title, full_text FROM all_articles')
    for row in cursor.fetchall():
        title_sentence=row[0]+". " # Turn article title into sentence
        full_text=row[1]
        all_text+=preprocess_article(title_sentence+full_text)

    cursor.close()
    sql_cxn.close()

    all_sentences=sent_tokenize(get_around_bug(all_text))

    with open('all_sentences.pickle', 'wb') as f:
        pickle.dump(all_sentences, f)

    return all_sentences


# Given all the sentences, indexes the most important words
def create_data_structures(all_sentences):
    # Data structures to be saved
    word_array=list() # list of individual words
    word_index=dict() # maps word to index in word_array

    # Create word rankings for word embedding
    word_counts=dict()
    for sen in all_sentences:
        tokens=word_tokenize(get_around_bug(sen))
        for tok in tokens:
            if tok not in word_counts:
                word_counts[tok]=1
            else:
                word_counts[tok]+=1

    rankings=list(word_counts.items())
    rankings.sort(reverse=True,key=lambda x: x[1])

    # Index all the words
    word_array=[x[0] for x in rankings[:max_vocab]]
    for i in range(len(word_array)):
        word_index[word_array[i]]=i

    with open('word_array.pickle', 'wb') as f:
        pickle.dump(word_array, f)
    with open('word_index.pickle', 'wb') as f:
        pickle.dump(word_index, f)

    return word_array, word_index


# Returns training distributions for each word in each sentence
def create_embedding_training(all_sentences, word_array, word_index):
    
    num_words=len(word_array)
    print("Processing data for {} words".format(num_words))

    training_examples=list() # List of distributions examples (for each word in each sentence)

    # Fill data structures
    with open("embedding_training.csv", 'w', newline='') as csv_file:
        csv_writer=csv.writer(csv_file)

        print("Creating embedding training examples")

        for sen in all_sentences:
            tokens=set(word_tokenize(get_around_bug(sen)))

            # Craft a training example - string->word presence in sentence
            # Bag of words very sparse, store indices of relevant words
            gold_label_indices=list()
            for tok in tokens:
                if tok in word_index:
                    gold_label_indices.append(word_index[tok])
            training_examples.append(gold_label_indices)
            csv_writer.writerow(gold_label_indices)

    print("Filled in embedding training examples")

    return training_examples


def full_setup():

    if exists('all_sentences.pickle'):
        with open('all_sentences.pickle', 'rb') as f:
            all_sentences=pickle.load(f)
    else:
        all_sentences=obtain_all_sentences()
    if exists('word_array.pickle') and exists('word_index.pickle'):
        with open('word_array.pickle', 'rb') as f:
            word_array=pickle.load(f)
        with open('word_index.pickle', 'rb') as f:
            word_index=pickle.load(f)
        if exists('embedding_training.csv'):
            with open('embedding_training.csv', 'r') as csv_file:
                csv_reader=csv.reader(csv_file, delimiter=',')
                training_examples=list()
                for row in csv_reader:
                    training_examples.append([int(x) for x in row])

        else:
            training_examples=create_embedding_training(all_sentences, word_array, word_index)
    else:
        word_array, word_index=create_data_structures(all_sentences)
        training_examples=create_embedding_training(all_sentences, word_array, word_index)

    return word_array, word_index, training_examples


if __name__ == "__main__":
    full_setup()