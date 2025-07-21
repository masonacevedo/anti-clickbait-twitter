import json

import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


model_path = "bad_tweets_model_1"

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained(model_path)

model.eval()

with open("val.json", "r") as f:
    val_tweets = json.load(f)

text = val_tweets[0].get('text')
print(f'Text: {text}')
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)

with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()

print(f"Prediction:", prediction)
print(f"Logits: {logits}")