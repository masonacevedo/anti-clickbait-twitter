import torch
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