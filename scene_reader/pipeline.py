from dataclasses import dataclass

from PIL import ImageOps

from scene_reader import config
from scene_reader.captioning import describe
from scene_reader.ocr import extract_text, has_text
from scene_reader.speech import speak
from scene_reader.translation import translate


@dataclass
class Result:
    source: str
    original: str
    translated: str
    audio_translated: str
    audio_original: str | None


def run(image, mode="auto", target_lang=config.TARGET_LANG, out_prefix="out"):
    img = ImageOps.exif_transpose(image)
    if mode == "scene":
        source, original = "scene", describe(img)
    else:
        text = extract_text(img).strip()
        if mode == "text" or has_text(text):
            source, original = "text", text or "No text found"
        else:
            source, original = "scene", describe(img)
    translated = translate(original, target=target_lang)
    audio_translated, audio_original = speak(translated, original, target_lang, out_prefix=out_prefix)
    return Result(source, original, translated, audio_translated, audio_original)