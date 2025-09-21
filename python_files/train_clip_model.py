from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch.nn.functional as F
import torch

device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

model.eval()
model.to(device)

