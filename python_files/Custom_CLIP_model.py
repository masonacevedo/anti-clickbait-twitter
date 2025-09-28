from transformers import CLIPModel, CLIPProcessor

import torch
import torch.nn as nn

class CustomCLIPModel(nn.Module):
    def __init__(self, clip_model,num_labels=3):
        super().__init__()
        self.clip_model = clip_model
        self.num_labels = num_labels

        clip_embedding_size = 512
        self.custom_layers = nn.Linear(2*clip_embedding_size, self.num_labels)



    def forward(self, input_ids, attention_mask, pixel_values):

        clip_outputs = self.clip_model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            pixel_values=pixel_values,
        )

        text_embeddings = clip_outputs.text_embeds
        image_embeddings = clip_outputs.image_embeds

        combined_embeddings = torch.cat([text_embeddings, image_embeddings], dim=1)

        return self.custom_layers(combined_embeddings)