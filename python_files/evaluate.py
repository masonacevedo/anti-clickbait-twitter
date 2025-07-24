import json

import torch
import torch.nn.functional as F
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification


model_path = "bad_tweets_model_2"

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained(model_path)

device = torch.device("mps" if torch.backends.mps.is_available else "cpu")
model = model.to(device)

model.eval()

with open("../val.json", "r") as f:
    val_tweets = json.load(f)

for t in val_tweets:
    text = t.get('text')
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()
        probabilities = F.softmax(logits, dim=1)

    print("\n\n\n")
    print(f'Begin Text:\n{text}\nEnd Text\n')
    print(f"Prediction:", prediction)
    print(f"Logits: {logits}")
    print(f"Probabilities: {probabilities}")
    print(f"List(probs):{probabilities[0].tolist()}")
    input()