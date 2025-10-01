import random
from transformers import CLIPModel, CLIPProcessor
from PIL import Image
import torch.nn.functional as F
import torch
import torch.nn as nn
from Custom_CLIP_model import CustomCLIPModel
from torch.utils.data import random_split, DataLoader
from tweet_dataset import TweetDataset
import matplotlib.pyplot as plt


model_path = input("Enter a name for the model:")
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

loss_function = nn.CrossEntropyLoss(torch.tensor([0.06429943951, 0.6116484183, 0.3240521422], dtype=torch.float32).to(device))
optimizer = torch.optim.Adam(myModel.parameters(), lr=1e-3)

file_path = "../labeled_tweets.json"
all_data = TweetDataset(file_path, processor)
training_data, validation_data = random_split(all_data, [0.8, 0.2])
training_dataset = DataLoader(training_data, batch_size=16, shuffle=True)
validation_dataset = DataLoader(validation_data, batch_size=16, shuffle=True)

loss_list = []
epoch_list = []
EPOCHS = 40
for epoch in range(0, EPOCHS):
    for index, data in enumerate(training_dataset):
        myModel.train()

        data['pixel_values'] = data['pixel_values'].squeeze(1).to(device)
        data['input_ids'] = data['input_ids'].to(device)
        data['attention_mask'] = data['attention_mask'].squeeze(1).to(device)
        data['label'] = data['label'].to(device)

        # input("Press Enter to continue...")
        labels = data['label']
        inputs = {k: v for k, v in data.items() if k in ['input_ids', 'attention_mask', 'pixel_values']}

        logits = myModel(**inputs)
        predictions = torch.argmax(logits, dim=1)

        loss = loss_function(logits, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    myModel.eval()
    with torch.no_grad():
        num_correct = 0
        num_seen = 0
        for batch, data in enumerate(validation_dataset):
            data['pixel_values'] = data['pixel_values'].squeeze(1).to(device)
            data['input_ids'] = data['input_ids'].to(device)
            data['attention_mask'] = data['attention_mask'].squeeze(1).to(device)
            data['label'] = data['label'].to(device)

            # input("Press Enter to continue...")
            labels = data['label']
            inputs = {k: v for k, v in data.items() if k in ['input_ids', 'attention_mask', 'pixel_values']}

            logits = myModel(**inputs)
            predictions = torch.argmax(logits, dim=1)

            num_correct += (predictions == labels).sum().item()
            num_seen += labels.size(0)

        accuracy = float(num_correct) / float(num_seen)
        print(f"Epoch {epoch} | Accuracy: {accuracy}")
    torch.save(myModel, f"models/{model_path}_{epoch}.pth")
    loss_list.append(loss.item())
    epoch_list.append(epoch)

plt.plot(epoch_list, loss_list)
plt.show()