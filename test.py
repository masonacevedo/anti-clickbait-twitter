import json

import torch
from torch.utils.data import Dataset
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

model_name = "distilbert-base-uncased"
tokenizer = DistilBertTokenizer.from_pretrained(model_name)
model = DistilBertForSequenceClassification.from_pretrained(model_name)

text = "claude would definitely hang out in the English teachers classroom during lunch"

inputs = tokenizer(text, return_tensors="pt")

with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits

prediction = torch.argmax(logits, dim=1).item()

print("Text:", text)
print("logits:", logits)
print("prediction:", prediction)

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
        label = int(item.get('score'))
        encoding['labels'] = torch.tensor(label)
        return encoding


dataset = TweetDataset('labeled_tweets.json', tokenizer)
print(dataset[0])