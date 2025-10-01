from flask import Flask, request, jsonify
from flask_cors import CORS
import torch
import torch.nn.functional as F
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, CLIPProcessor
import requests
from torchvision import transforms

from PIL import Image
from io import BytesIO

print("what is going on here")

processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

# model_path = "bad_tweets_model_1"
tokenizer = DistilBertTokenizer.from_pretrained("distilbert-base-uncased")
model = torch.load("models/attempt_1_39.pth", weights_only=False)

device = torch.device("mps" if torch.backends.mps.is_available else "cpu")
model = model.to(device)

model.eval()

app = Flask(__name__)
CORS(app)

import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def make_predction(text, image_link):
    if image_link is not None:
        app.logger.info(f"Fetching image from: {image_link}")
        resp = requests.get(url=image_link, stream=True)
        pil_image = Image.open(BytesIO(resp.content))
    else:
        pil_image = None
    try:
        encoding = processor(
            text=text,
            images=pil_image,
            return_tensors="pt",
            padding="max_length",
            truncation=True
        )
    except Exception as e:
        app.logger.error(f"Error processing text: {text}")
        app.logger.error(f"Exception: {e}", exc_info=True)
        return 0


    if "pixel_values" not in encoding:
        encoding['pixel_values'] = torch.zeros(1, 3, 224, 224)

    encoding['pixel_values'] = encoding['pixel_values'].squeeze(1).to(device)
    encoding['input_ids'] = encoding['input_ids'].to(device)
    encoding['attention_mask'] = encoding['attention_mask'].squeeze(1).to(device)

    with torch.no_grad():
        logits = model(**encoding)
        probabilities = F.softmax(logits, dim=1)

    class_1_prob = probabilities[0].tolist()[1]
    class_2_prob = probabilities[0].tolist()[2]

    score = max(class_1_prob, class_2_prob)
    if score < 0.2:
        return 0
    else:
        return score


@app.route('/evaluate', methods=['POST'])
def predict():
    app.logger.info("predicting")
    tweet = request.json['text']
    if 'image_link' in request.json:
        image_link = request.json['image_link']
    else:
        image_link = None

    app.logger.info(f"Evaluating tweet: {tweet[:50]}...")
    score = make_predction(tweet, image_link)
    app.logger.info(f"Score: {score}")
    return jsonify({'score': score})

if __name__ == "__main__":
    app.run(debug=True)