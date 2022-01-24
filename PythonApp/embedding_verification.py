import csv
import numpy as np
from os.path import exists


def load_word_embeddings():
    # Store all word2vec relationships
    word_vectors=dict()

    if exists('word_embedding.csv'):

        csv_file=open('word_embedding.csv', 'r')
        csv_reader=csv.reader(csv_file, delimiter=',')

        for row in csv_reader:
            word=row[0]
            word_vector=[float(x) for x in row[1:]]
            word_vectors[word]=np.array(word_vector)

        return word_vectors

def rank_by_distance(add_word, subtract_word, word2vec):

    word_vector=np.zeros(100)
    add_word=set(add_word)
    subtract_word=set(subtract_word)


    for word in add_word:
        if word in word2vec:
            word_vector+=word2vec[word]
    for word in subtract_word:
        if word in word2vec:
            word_vector-=word2vec[word]

    # Calculate every other word's distance from input word
    distances=dict()
    for word_key in word2vec.keys():
        if word_key not in add_word and word_key not in subtract_word:
            distances[word_key]=abs(np.linalg.norm(word_vector-word2vec[word_key]))

    # Return a ranked list of all words by distance
    word_distances=list(distances.items())
    word_distances.sort(key=lambda x: x[1])

    return [x[0] for x in word_distances]

if __name__=="__main__":
    word2vec=load_word_embeddings()

    print("What is a king who is not a man but a woman?")
    r1=rank_by_distance(["king", "woman"],["man"],word2vec)
    print(r1[:10])

    print("What is the dollar without the US but in the UK?")
    r2=rank_by_distance(["dollar", "UK"],["US"],word2vec)
    print(r2[:10])

    print("What do these things have in common with green?")
    r3=rank_by_distance(["green"], [], word2vec)
    print(r3[:10])