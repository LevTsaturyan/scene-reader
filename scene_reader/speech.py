import wave
from functools import lru_cache
from pathlib import Path

from gtts import gTTS

from scene_reader import config
from scene_reader.translation import detect_lang

VOICES = {"ru": "ru_RU-irina-medium", "en": "en_US-lessac-medium"}


@lru_cache(maxsize=2)
def _piper_voice(lang):
    from piper import PiperVoice
    return PiperVoice.load(Path(config.PIPER_DIR) / f"{VOICES[lang]}.onnx")


def _synthesize(text, lang, base):
    if config.TTS_ENGINE == "piper":
        path = f"{base}.wav"
        with wave.open(path, "wb") as wav:
            _piper_voice(lang).synthesize_wav(text, wav)
        return path
    path = f"{base}.mp3"
    gTTS(text, lang=lang).save(path)
    return path


def _try_synthesize(text, lang, base):
    """Ошибка озвучки не должна мешать показать распознанный текст."""
    try:
        return _synthesize(text, lang, base)
    except Exception as error:
        print(f"Озвучка не удалась: {error}")
        return None


def speak(translated, original, target, out_prefix="out"):
    translated_path = _try_synthesize(translated, target, f"{out_prefix}_translated")
    original_path = None
    if original != translated:
        original_path = _try_synthesize(original, detect_lang(original), f"{out_prefix}_original")
    return translated_path, original_path