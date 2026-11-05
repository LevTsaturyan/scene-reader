from functools import lru_cache

import easyocr
import numpy as np
from PIL import Image, ImageOps
import pytesseract
import torch

from scene_reader import config


@lru_cache(maxsize=1)
def _load_easyocr():
    return easyocr.Reader(list(config.EASYOCR_LANGS), gpu=torch.cuda.is_available(), verbose=False)


def extract_text(img: Image.Image, engine: str = config.OCR_ENGINE) -> str:
    if engine == "tesseract":
        return extract_tesseract(img)
    return extract_easyocr(img)


def extract_easyocr(img: Image.Image, min_confidence: float = config.OCR_MIN_CONFIDENCE) -> str:
    results = _load_easyocr().readtext(np.array(img.convert("RGB")))
    return "\n".join(text for _, text, confidence in results if confidence >= min_confidence)


def extract_tesseract(img: Image.Image, langs: str = config.OCR_LANGS) -> str:
    return pytesseract.image_to_string(preprocess(img), lang=langs)


def has_text (text: str, min_words: int = config.MIN_WORDS) -> bool: #достаточно ли слов для наличия текста
     return len(text.split()) >= min_words


def preprocess(img: Image.Image) -> Image.Image: #    Серое изображение + автоконтраст
    gray = ImageOps.grayscale(img)
    return ImageOps.autocontrast(gray)
