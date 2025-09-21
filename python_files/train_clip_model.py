from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch.nn.functional as F
import torch
from Custom_CLIP_model import CustomCLIPModel


torch.manual_seed(42)
device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

for param in clip_model.parameters():
    param.requires_grad = False

myModel = CustomCLIPModel(clip_model, num_labels=3)
myModel.to(device)


trainable_params = sum(p.numel() for p in myModel.parameters() if p.requires_grad)
total_params = sum(p.numel() for p in myModel.parameters())

print(f"Trainable parameters: {trainable_params:,}")
print(f"Total parameters: {total_params:,}")
print(f"Percentage trainable: {100 * trainable_params / total_params:.2f}%")

loss_function = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(myModel.parameters(), lr=1e-3)


EPOCHS = 10
for epoch in range(0, EPOCHS):
    pass