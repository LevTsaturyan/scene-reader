import pytest

from PIL import Image

from scene_reader import ocr
from scene_reader.ocr import has_text
from scene_reader.translation import detect_lang, normalize_case, split_chunks


class FakeTokenizer:
    def tokenize(self, text):
        return text.split()


@pytest.mark.parametrize("text, expected", [
    ("раз два", False),
    ("раз два три", True),
    ("", False),
])
def test_has_text(text, expected):
    assert has_text(text, min_words=3) == expected


@pytest.mark.parametrize("text, expected", [
    ("Привет", "ru"),
    ("Hello", "en"),
    ("", "en"),
])
def test_detect_lang(text, expected):
    assert detect_lang(text) == expected


def test_normalize_case_only_changes_caps_lines():
    assert normalize_case("ВЫХОД\nNormal Text") == "Выход\nNormal Text"


def test_split_chunks_respects_token_limit():
    chunks = split_chunks("один два. три четыре. пять шесть.", FakeTokenizer(), max_tokens=4)
    assert chunks == ["один два. три четыре.", "пять шесть."]

def test_easyocr_filters_low_confidence(monkeypatch):
    class FakeReader:
        def readtext(self, image):
            return [(None, "ВЫХОД", 0.9), (None, "мусор", 0.1)]

    monkeypatch.setattr(ocr, "_load_easyocr", lambda: FakeReader())
    assert ocr.extract_easyocr(Image.new("RGB", (10, 10)), min_confidence=0.5) == "ВЫХОД"


@pytest.mark.parametrize("engine, expected", [
    ("easyocr", "из easyocr"),
    ("tesseract", "из tesseract"),
])
def test_extract_text_selects_engine(monkeypatch, engine, expected):
    monkeypatch.setattr(ocr, "extract_easyocr", lambda img: "из easyocr")
    monkeypatch.setattr(ocr, "extract_tesseract", lambda img: "из tesseract")
    assert ocr.extract_text(Image.new("RGB", (10, 10)), engine=engine) == expected
