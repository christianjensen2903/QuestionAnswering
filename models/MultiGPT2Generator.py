# from os import pread
import imp
from transformers import BloomTokenizerFast, BloomForCausalLM, Trainer, TrainingArguments, DataCollatorForLanguageModeling
from models.Model import Model
from models.feature_extraction.feature_extracion import feature_extraction
from datasets import Dataset
import torch
import math

# -- Resources --
# https://huggingface.co/Finnish-NLP/gpt2-finnish
# https://www.modeldifferently.com/en/2021/12/generación-de-fake-news-con-gpt-2/
# https://github.com/huggingface/transformers/issues/1528#issuecomment-544977912


class MultiGPT2Generator(Model, feature_extraction):
    def __init__(self):
        super().__init__()
        if torch.cuda.is_available():
            self.device = "cuda:0"
        else:
            self.device = "cpu"

        self.set_language("english")

    def set_language(self, language):
        super().set_language(language)
        pretrained_name = "bigscience/bloom-560m"
        self.tokenizer = BloomTokenizerFast.from_pretrained(pretrained_name)
        self.model = BloomForCausalLM.from_pretrained(
            pretrained_name,
            output_hidden_states=True
        )
        self.training_args = TrainingArguments(
            output_dir=self.get_save_path(),
            num_train_epochs=3,
            per_device_train_batch_size=1,
            per_device_eval_batch_size=1,
            warmup_steps=200,
            weight_decay=0.01,
            prediction_loss_only=True,
            save_steps=10000
        )
        self.data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )

    def extract_X(self, dataset):
        train_dataset = Dataset.from_pandas(
            dataset[['question_text', 'document_plaintext']])

        def tokenize_function(examples):
            input_str = 'Question: ' + \
                examples['question_text'] + '\nContext: ' + \
                examples['document_plaintext']
            return self.tokenizer(
                input_str,
                padding="max_length", 
                truncation=True
            )

        tokenized_train_dataset = train_dataset.map(
            tokenize_function,
            remove_columns=['question_text', 'document_plaintext'],
        )

        return tokenized_train_dataset

    def get_perplexity(self, X):
        if not hasattr(self, 'trainer'):
            self.trainer = Trainer(
                model=self.model,
                args=self.training_args,
                data_collator=self.data_collator,
                train_dataset=X,
                eval_dataset=X
            )
        return math.exp(self.trainer.evaluate()['eval_loss'])

    def train(self, X, y):
        self.trainer = Trainer(
            model=self.model,
            args=self.training_args,
            data_collator=self.data_collator,
            train_dataset=X
        )
        self.trainer.train()

    def generate_text(self, X, num_return_sequences=5, max_length=50):
        self.model.eval()
        self.model.to(self.device)
        text_ids = self.tokenizer.encode(X, return_tensors='pt')

        generated_text_samples = self.model.generate(
            text_ids,
            do_sample=True,
            max_length=max_length,
            num_return_sequences=num_return_sequences
        )

        for i, model_output in enumerate(generated_text_samples):
            print(
                f"{i}: {self.tokenizer.decode(model_output, skip_special_tokens=True)}"
            )

    def predict(self, X):
        self.model.eval()
        self.model.to(self.device)

        def get_last_hidden_state(row):
            row['last_hidden_state'] = self.model(
                torch.tensor(row['input_ids'], device=self.device)
            )[2][-1][0][-1]
            return row

        with torch.no_grad():
            return (X.map(get_last_hidden_state)['last_hidden_state'])

    def save(self):
        path = self.get_save_path()
        self.trainer.save_model(path)
        self.tokenizer.save_pretrained(path)

    def load(self):
        path = self.get_save_path()
        self.tokenizer = BloomTokenizerFast.from_pretrained(path)
        self.model = BloomForCausalLM.from_pretrained(path)
