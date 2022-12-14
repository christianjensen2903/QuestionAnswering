from models.Model import Model
from xgboost import XGBClassifier as XGB_model
from pickle import dump, load
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import pandas as pd

class XGBoost(Model):
    def __init__(self):
        super().__init__()
        self.model = XGB_model(objective='binary:logistic', random_state=43)

    def train(self, X, y):
        self.model = self.model.fit(X, y)

    def predict(self, X):
        pass

    def evaluate(self, X, y):
        return self.model.score(X, y)

    def save(self):
        dump(self.model, open(self.get_save_path('pkl'), 'wb'))

    def load(self):
        self.model = load(open(self.get_save_path('pkl'), 'rb'))
    
    def weights(self):
        return dict(zip(
            [f'*QUESTION* {x}' for x in self.question_vectorizer.vocabulary_] +
            [f'*PLAINTEXT* {x}' for x in self.plaintext_vectorizer.vocabulary_] +
            [f'*FIRSTWORD* {x}' for x in self.first_word_vectorizer.vocabulary_] +
            ['*OVERLAP*'] +
            [f'*QUESTION_CONTINOUS* {x}' for x in range(100)] +
            [f'*PLAINTEXT_CONTINOUS* {x}' for x in range(100)] +
            ['*EUCLIDEAN*'] +
            ['*COSINE*'] +
            ['*BERT_SCORE*'],
            list(self.model.feature_importances_),
        ))


    def explainability(self , X , y , n = 10):
        most_important = sorted(self.weights().items(), key=lambda item: abs(item[1]), reverse=True)[:n]
        names , values = list(zip(*most_important))

        plot_df = pd.DataFrame()
        plot_df['names'] = names
        plot_df['values'] = values
        plot_df.plot( x = 'names' , y = 'values', kind='bar' , figsize=(20,10))
        plt.xticks(fontsize = 15)
        plt.show()

        print (
            "EXPLAINABILITY:\n",
            "Top {} most important features:\n".format(n),
            sorted(self.weights().items(), key=lambda item: item[1], reverse=True)[:n], # n most important
            "\n\n",
            "Top {} least important features:\n".format(n),
            sorted(self.weights().items(), key=lambda item: item[1], reverse=False)[:n] # n least important
            )
        print(f'Confusion_matrix Matrix:', confusion_matrix(y , self.model.predict(X) , normalize = "all"))