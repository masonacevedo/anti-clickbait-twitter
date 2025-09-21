from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch.nn.functional as F
import torch

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

model.eval()

image_path = "../images/GwOarDwWcAAOGL9.jpg"
image = Image.open(image_path)

image_inputs = processor(images=[image], return_tensors="pt")
image_outputs = model.get_image_features(**image_inputs)

text_inputs = processor(text="Zendaya hanging out with some friends.", return_tensors="pt")
text_outputs = model.get_text_features(**text_inputs)


text_and_image_similarity = F.cosine_similarity(image_outputs, text_outputs, dim=1)
print("Cosine similarity between text and image:", text_and_image_similarity)

random_tensor = torch.rand_like(image_outputs)
random_tensor_and_text_similarity = F.cosine_similarity(random_tensor, text_outputs, dim=1)
print("Cosine similarity between random tensor and text:", random_tensor_and_text_similarity)

random_tensor_and_image_similarity = F.cosine_similarity(random_tensor, image_outputs, dim=1)
print("Cosine similarity between random tensor and image:", random_tensor_and_image_similarity)

