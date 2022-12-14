from gensim.models import Word2Vec as GensimWord2Vec
from models.Model import Model
from models.feature_extraction.feature_extracion import feature_extraction
import numpy as np


class Word2Vec(Model,feature_extraction):
    def __init__(self):
        super().__init__()

    def extract_X(self, dataset):
        return dataset['tokenized_question'].to_list() + dataset['tokenized_plaintext'].to_list()

    def train(self, X):
        self.model = GensimWord2Vec(X, min_count=1)

    def predict(self, X):
        # Handle words missing from the vocabulary
        output = np.array([
            self.model.wv[word] if word in self.model.wv else np.zeros(self.model.vector_size) for word in X
        ])
        # If all words are missing, return a zero vector
        return output

    def evaluate(self, X, y):
        pass

    def save(self):
        self.model.save(self.get_save_path('model'))

    def load(self):
        self.model = GensimWord2Vec.load(self.get_save_path('model'))
