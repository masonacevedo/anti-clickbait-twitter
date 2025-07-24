import json

import torch
from torch.utils.data import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, TrainingArguments, Trainer

from sklearn.model_selection import train_test_split

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")


class DistilBertForBoundedRegression(DistilBertForSequenceClassification):
    def forward(self, *args, **kwargs):
        output = super().forward(*args, **kwargs)
        output.logits = torch.sigmoid(output.logits)
        return output


model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForBoundedRegression.from_pretrained(model_name, num_labels=1)


class TweetDataset(Dataset):
    def __init__(self, json_path, tokenizer, max_length=128):
        with open(json_path, "r") as f:
            self.data = json.load(f)
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        encoding = self.tokenizer(
            item.get('text'),
            truncation=True,
            padding="max_length",
            max_length=self.max_length,
            return_tensors="pt"
        )
        encoding = {k: v.squeeze(0) for k, v in encoding.items()}
        label_map = {"0": float(0.0), "1": float(0.5), "2": float(1.0)}
        label = float(label_map[item.get('score')])
        encoding['labels'] = torch.tensor(label)
        return encoding


dataset = TweetDataset('../labeled_tweets.json', tokenizer)

training_dataset = TweetDataset("../train.json", tokenizer)
validation_dataset = TweetDataset("../val.json", tokenizer)

training_args = TrainingArguments(
    output_dir = "./results",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    eval_strategy="epoch",
    save_strategy="epoch",
    logging_dir="./logs",
    logging_steps=10,
    load_best_model_at_end=True,
    metric_for_best_model="eval_loss",
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=training_dataset,
    eval_dataset=validation_dataset
)

print("Trainer device:", trainer.args.device)

trainer.train()

trainer.save_model("bad_tweets_model_2")