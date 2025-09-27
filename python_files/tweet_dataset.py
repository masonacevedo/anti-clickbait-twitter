from torch.utils.data import Dataset
import json
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import torch

class TweetDataset(Dataset):
    def __init__(self, json_path, processor, max_length=128):
        with open(json_path, "r") as f:
            self.data = json.load(f)
        self.processor = processor
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        text = item.get('text')
        # note: this only processes the first image. 
        #    it would be better to utilize all images in the future.
        has_image = False
        if len(item.get('images')) > 0:
            image_url = item.get('images')[0]
            image_name = image_url.split("/")[-1]
            image_location = "../images/" + image_name
            try:
                image = Image.open(image_location)
                has_image = True
            except FileNotFoundError:
                print(f"Image {image_location} not found")
                image = None
        else:
            image = None

        encoding = self.processor(
            text=text,
            images=image,
            return_tensors="pt",
            padding="max_length",
            truncation=True
        )
        if 'pixel_values' not in encoding:
            encoding['pixel_values'] = torch.zeros(1, 3, 224, 224)
        encoding['has_image'] = torch.tensor([1.0 if has_image else 0.0])
        return encoding

if __name__ == "__main__":
    CLIPProcessor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    dataset = TweetDataset("../bookmarked_tweets_v5.json", CLIPProcessor)
    for item in dataset:
        print("item:", item)
        # Extract only the fields that CLIP model expects
        clip_inputs = {k: v for k, v in item.items() if k in ['input_ids', 'attention_mask', 'pixel_values']}
        print("model(**clip_inputs):", model(**clip_inputs))
        input("Press Enter to continue...")