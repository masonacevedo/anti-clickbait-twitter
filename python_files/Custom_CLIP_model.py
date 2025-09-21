from transformers import CLIPModel, CLIPProcessor

import torch
import torch.nn as nn

class CustomCLIPModel(nn.Module):
    def __init__(self, clip_model,num_labels=3):
        super().__init__()
        self.clip_model = clip_model
        self.num_labels = num_labels

        clip_embedding_size = 512
        self.custom_layers = nn.Sequential(
            nn.Linear(2*clip_embedding_size, 64),
            nn.ReLU(),
            nn.Linear(64, self.num_labels),
        )


    def forward(self, tokens, attention_mask, images):

        clip_outputs = self.clip_model(
            input_ids=tokens,
            attention_mask=attention_mask,
            pixel_values=images,
        )

        text_embeddings = clip_outputs.text_embeds
        image_embeddings = clip_outputs.image_embeds

        combined_embeddings = torch.cat([text_embeddings, image_embeddings], dim=1)

        return self.custom_layers(combined_embeddings)

clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
myModel = CustomCLIPModel(clip_model)

print(myModel)