import numpy as np
import torch
import torch.nn as nn
from torch.nn import init
import torch.optim as optim
import math
import random
import pickle
import time
import csv
from tqdm import tqdm
from word_embedding_setup import full_setup

"""
    Very simple feed forward neural network class
    Task: For each word (one-hot vector), recreate a distribution
    of the other words normally found around it.
"""
class EmbeddingNN(nn.Module):
    def __init__(self, num_words, embed_size):
            super(EmbeddingNN, self).__init__()
            self.num_words=num_words
            self.embed_size = embed_size
            self.W1 = nn.Linear(num_words, embed_size)
            self.activation = nn.ReLU()
            self.W2 = nn.Linear(embed_size, num_words)
            self.loss = nn.L1Loss()

    def compute_Loss(self, predicted_vector, gold_label):
        return self.loss(predicted_vector, gold_label)

    def forward(self, input_vector):
        input_vector = torch.from_numpy(input_vector).float()
        embed_layer = self.W1(input_vector)
        predicted_vector = self.W2(embed_layer)
        return predicted_vector

    def generate_embedding(self, input_vector):
        input_vector = torch.from_numpy(input_vector).float()
        embedding = self.W1(input_vector)
        return embedding # Captures internal information about represented word

"""
    Given metaparameters, trains the neural network on the data.
"""
def train_on_data(embed_size, number_of_epochs):

    # Fetch data for training embedding
    print("Fetching data")
    word_array, word_index, training_examples = full_setup()
    print("Fetched and indexed data")

    random.shuffle(training_examples)
    training_set=training_examples[:round(0.9*len(training_examples))]
    validation_set=training_examples[round(0.9*len(training_examples)):]
    print("Created training and validation sets")

    #Create the model
    model = EmbeddingNN(num_words=len(word_array), embed_size=embed_size)
    # This network is trained by traditional (batch) gradient descent
    optimizer = optim.SGD(model.parameters(),lr=0.01, momentum=0.9)

    print("Training model of {} embeddings for {} epochs".format(len(word_array),number_of_epochs))
    print("Commencing training")
    for epoch in range(number_of_epochs):
        model.train()
        optimizer.zero_grad()
        start_time = time.time()

        minibatch_size = 8
        total_loss=0
        N = len(training_set)
        print("Training started for epoch {}".format(epoch + 1))
        for minibatch_index in tqdm(range(N // minibatch_size)):
            optimizer.zero_grad()
            loss = None
            for example_index in range(minibatch_size):
                # Form training example
                example = training_set[minibatch_index * minibatch_size + example_index]
                input_vector = np.zeros(len(word_array))
                for i in example:
                    input_vector[i]=1 # Creating bag of words vector for training

                gold_label = input_vector # Recreating bags of words forces capture of information

                # Compare with model output
                predicted_vector = model(input_vector)
                example_loss = model.compute_Loss(predicted_vector.view(1,-1), torch.tensor(np.array([gold_label]), dtype=torch.long))
                if loss is None:
                    loss = example_loss
                else:
                    loss += example_loss
                total_loss+=example_loss
            loss = loss / minibatch_size
            loss.backward()
            optimizer.step()
        print("Training completed for epoch {}".format(epoch + 1))
        print("Average loss for epoch {}: {}".format(epoch + 1, total_loss / N))
        print("Training time for this epoch: {}".format(time.time() - start_time))

        model.train(mode=False)
        total_loss=0
        start_time = time.time()
        print("Validation started for epoch {}".format(epoch + 1))
        N = len(validation_set)
        for minibatch_index in tqdm(range(N // minibatch_size)):
            for example_index in range(minibatch_size):
                # Form validation example
                example = validation_set[minibatch_index * minibatch_size + example_index]
                input_vector = np.zeros(len(word_array))
                for i in example:
                    input_vector[i]=1

                gold_label = input_vector

                # Compare with model output
                predicted_vector = model(input_vector)
                example_loss = model.compute_Loss(predicted_vector.view(1,-1), torch.tensor(np.array([gold_label]), dtype=torch.long))
                
                total_loss+=example_loss
        print("Validation completed for epoch {}".format(epoch + 1))
        print("Average loss for epoch {}: {}".format(epoch + 1, total_loss / N))
        print("Validation time for this epoch: {}".format(time.time() - start_time))

    pickle.dump(model, open("embedding_model.pickle", 'wb'))

    return model, word_array

def generate_embeddings(model, words):
    print("Found data on {} words".format(len(words)))
    print("Generating word embeddings")
    with open('word_embedding.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        for i in range(len(words)):
            input_vector=np.zeros(len(words))
            input_vector[i]=1
            #embedding=nn.functional.normalize(model.generate_embedding(input_vector), dim=0).tolist()
            embedding=model.generate_embedding(input_vector).tolist()
            embedding.insert(0, words[i])
            writer.writerow(embedding)
    print("Word embeddings completed")

"""
    This creates and trains models according to my fine-tuning
"""
if __name__ == "__main__":
    from os.path import exists

    if not exists('embedding_model.pickle'):
        model, words=train_on_data(100, 10)
        generate_embeddings(model, words)
    elif not exists('word_embedding.csv'):
        words=pickle.load(open('word_array.pickle', 'rb'))
        model=pickle.load(open('embedding_model.pickle', 'rb'))
        generate_embeddings(model, words)