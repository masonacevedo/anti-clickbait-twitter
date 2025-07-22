from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

model_path = "bad_tweets_model_1"

tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = DistilBertForSequenceClassification.from_pretrained(model_path)

device = torch.device("mps" if torch.backends.mps.is_available else "cpu")
model = model.to(device)

model.eval()

app = Flask(__name__)
CORS(app)

def make_predction(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        prediction = torch.argmax(logits, dim=1).item()
        probabilities = F.softmax(logits, dim=1)

    class_1_prob = probabilities[0].tolist()[1]
    class_2_prob = probabilities[0].tolist()[2]
    
    return max(class_1_prob, class_2_prob)


@app.route('/evaluate', methods=['POST'])
def predict():
    tweet = request.json['text']
    score = make_predction(tweet)
    return jsonify({'score': score})

if __name__ == "__main__":
    app.run(debug=True)