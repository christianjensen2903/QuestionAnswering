from abc import ABC, abstractmethod
import os
import torch


class Model(ABC):

    def __init__(self, language: str = "english", config: dict = {}):
        super().__init__()

        self.language = language.lower()

        self.config = config

        # Set the device to use
        if torch.cuda.is_available():
            self.device = torch.device("cuda")
        else:
            self.device = torch.device("cpu")
            

    def get_save_path(self, filetype: str = ''):
        """Get the path of the model for loading and saving"""
        # Get the path of type saved_models/model_type
        path = os.path.join(
            'saved_models',
            self.__class__.__name__
        )
        # Create the directory if it doesn't exist
        os.makedirs(path, exist_ok=True)

        # Return the path of type saved_models/model_type/language.filetype
        # Or saved_models/model_type/language if the saving is done on a directory
        return os.path.join(
            path,
            f'{self.language}.{filetype}' if filetype else self.language
        )

    def extract_X(self, train_data):
        """Extract the X values from the dataset"""
        pass

    def extract_y(self, train_data):
        """Extract the y values from the dataset"""
        pass

    def train(self, X, y):
        """Train the model"""
        pass

    def predict(self, X):
        """Predict the answer"""
        pass

    def evaluate(self, X, y):
        """Evaluate the model"""
        pass

    def save(self):
        """Save the model"""
        pass

    def load(self):
        """Load the model"""
        pass

    def weights(self):
        """Gets the model weights as a dictionary"""
        pass

    def explainability(self):
        """Use an use an interpretability method on the model"""
        pass