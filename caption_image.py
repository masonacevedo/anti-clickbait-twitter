from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base", use_fast=True)
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")


with open("image_names.txt", "r") as f:
    names = f.readlines()
    for name in names:
        img = Image.open(f"images/{name}".replace("\n", ""))
        inputs = processor(img, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        print(name)
        print(caption)
        input()
