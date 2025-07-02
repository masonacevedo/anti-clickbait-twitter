from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image

processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

img = Image.open("images/tweet_1919791768972693510_13_1915508916017868800.jpg")

inputs = processor(img, return_tensors="pt")
out = model.generate(**inputs)

caption = processor.decode(out[0], skip_special_tokens=True)
print(caption)