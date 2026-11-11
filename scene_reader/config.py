import os

TARGET_LANG = os.getenv("SCENE_READER_TARGET_LANG", "ru")
OCR_ENGINE = os.getenv("SCENE_READER_OCR_ENGINE", "easyocr")
OCR_LANGS = os.getenv("SCENE_READER_OCR_LANGS", "rus+eng")
EASYOCR_LANGS = ("ru", "en")
OCR_MIN_CONFIDENCE = float(os.getenv("SCENE_READER_OCR_MIN_CONFIDENCE", "0.5"))
MIN_WORDS = int(os.getenv("SCENE_READER_MIN_WORDS", "1"))
OCR_MAG_RATIO = float(os.getenv("SCENE_READER_OCR_MAG_RATIO", "1.0"))
TTS_ENGINE = os.getenv("SCENE_READER_TTS_ENGINE", "gtts")  # gtts или piper
PIPER_DIR = os.getenv("SCENE_READER_PIPER_DIR", "models/piper")