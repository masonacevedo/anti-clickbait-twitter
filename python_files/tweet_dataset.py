from torch.utils.data import Dataset
import json
from PIL import Image

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
        if len(item.get('images')) > 0:
            image_url = item.get('images')[0]
            image_name = image_url.split("/")[-1]
            image_location = "../images/" + image_name
            image = Image.open(image_location)
        else:
            image = None

        encoding = self.processor(
            text=text,
            image=image,
            return_tensors="pt",
            padding="max_length",
            truncation=True
        )
        return encoding
