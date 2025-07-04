import json
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large", use_fast=True)
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

captioned_tweets_file_name = "captioned_tweets.json"
with open(captioned_tweets_file_name, "r") as f:
    all_captioned_tweets = json.load(f)

with open("bookmarked_tweets_v2.json", "r") as f:
    tweets = json.load(f)
    for tweet in tweets:

        if tweet["media"] != []:
            img = Image.open(tweet["media"][0]["path"])
            inputs = processor(img, return_tensors="pt")
            out = model.generate(**inputs)
            caption = processor.decode(out[0], skip_special_tokens=True)
            print("successfully generated a caption")
        else:
            caption = "N/A"

        tweet["caption"] = caption
        with open(captioned_tweets_file_name, "w") as f2:
            all_captioned_tweets.append(tweet)
            json.dump(all_captioned_tweets, f2, indent=2)
        print("successfully saved a captioned tweet")

