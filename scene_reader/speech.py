from gtts import gTTS

from scene_reader.translation import detect_lang


def speak(translated, original, target, out_prefix="out"):
    translated_path = f"{out_prefix}_translated.mp3"
    gTTS(translated, lang=target).save(translated_path)

    original_path = None
    if original != translated:
        original_path = f"{out_prefix}_original.mp3"
        gTTS(original, lang=detect_lang(original)).save(original_path)

    return translated_path, original_path