from functools import lru_cache

import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

MODEL_NAME = "Salesforce/blip-image-captioning-base"


@lru_cache(maxsize=1)
def _load():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    processor = BlipProcessor.from_pretrained(MODEL_NAME)
    model = BlipForConditionalGeneration.from_pretrained(MODEL_NAME).to(device)
    model.eval()
    return processor, model, device

def describe(img, max_new_tokens=30, num_beams=3):
    processor, model, device = _load()
    inputs = processor(images=img.convert("RGB"), return_tensors="pt").to(device)
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=max_new_tokens, num_beams=num_beams)
    return processor.decode(out[0], skip_special_tokens=True)