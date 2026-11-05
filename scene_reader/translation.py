from functools import lru_cache
import torch
from transformers import MarianMTModel, MarianTokenizer
import re

MAX_TOKENS = 400

def detect_lang(text):
    cyr = sum(1 for ch in text.lower() if "а" <= ch <= "я" or ch == "ё")
    lat = sum(1 for ch in text.lower() if "a" <= ch <= "z")
    return "ru" if cyr > lat else "en"

@lru_cache(maxsize=2)
def _load(src, tgt):
    name = f"Helsinki-NLP/opus-mt-{src}-{tgt}"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = MarianTokenizer.from_pretrained(name)
    model = MarianMTModel.from_pretrained(name).to(device)
    model.eval()
    return tokenizer, model, device


def translate(text, target="ru"):
    text = normalize_case(text)
    src = detect_lang(text)
    if src == target:
        return text
    tokenizer, model, device = _load(src, target)
    chunks = split_chunks(text, tokenizer)
    inputs = tokenizer(chunks, return_tensors="pt", padding=True, truncation=True).to(device)
    with torch.inference_mode():
        out = model.generate(**inputs)
    return " ".join(tokenizer.batch_decode(out, skip_special_tokens=True))


def split_chunks(text, tokenizer, max_tokens=MAX_TOKENS):
    sentences = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    chunks = []
    current = ""
    for sent in sentences:
        candidate = (current + " " + sent).strip()
        if len(tokenizer.tokenize(candidate)) <= max_tokens:
            current = candidate
        else:
            if current:
                chunks.append(current)
            current = sent
    if current:
        chunks.append(current)
    return chunks

def normalize_case(text):
    lines = text.split("\n")
    return "\n".join(line.capitalize() if line.isupper() else line for line in lines)