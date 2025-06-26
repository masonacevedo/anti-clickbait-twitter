import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

model_name = "elozano/bert-base-cased-clickbait-news"
tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForSequenceClassification.from_pretrained(model_name)

model.to(device)
model.eval()

text = "This is fine"

inputs = tokenizer(text, return_tensors="pt").to(device)

with torch.no_grad():
    outputs = model(**inputs)
    logits = outputs.logits
    prediction = torch.argmax(logits, dim=1).item()

print("Text:", text)
print("logits:", logits)
print("prediction:", prediction)

