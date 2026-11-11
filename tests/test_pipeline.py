import pytest
from PIL import Image

from scene_reader import pipeline


@pytest.fixture
def img():
    return Image.new("RGB", (10, 10))


@pytest.fixture(autouse=True)
def fakes(monkeypatch):
    monkeypatch.setattr(pipeline, "describe", lambda img: "a brick wall")
    monkeypatch.setattr(pipeline, "translate", lambda text, target: f"[{target}] {text}")
    monkeypatch.setattr(pipeline, "speak", lambda translated, original, target, out_prefix: ("t.mp3", "o.mp3"))


def set_ocr(monkeypatch, text):
    monkeypatch.setattr(pipeline, "extract_text", lambda img: text)


def test_auto_with_text_uses_ocr(monkeypatch, img):
    set_ocr(monkeypatch, "раз два три")
    result = pipeline.run(img)
    assert result.source == "text"
    assert result.original == "раз два три"


def test_auto_without_text_uses_blip(monkeypatch, img):
    set_ocr(monkeypatch, "  ")
    result = pipeline.run(img)
    assert result.source == "scene"
    assert result.original == "a brick wall"


def test_scene_mode_skips_ocr(monkeypatch, img):
    def fail(*args, **kwargs):
        raise AssertionError("OCR не должен вызываться")

    monkeypatch.setattr(pipeline, "extract_text", fail)
    assert pipeline.run(img, mode="scene").source == "scene"


def test_text_mode_without_text_says_not_found(monkeypatch, img):
    set_ocr(monkeypatch, "")
    result = pipeline.run(img, mode="text")
    assert result.source == "text"
    assert result.original == "No text found"


def test_result_has_translation_and_audio(monkeypatch, img):
    set_ocr(monkeypatch, "раз два три")
    result = pipeline.run(img, target_lang="en")
    assert result.translated == "[en] раз два три"
    assert result.audio_translated == "t.mp3"
    assert result.audio_original == "o.mp3"



def test_exif_rotation_is_applied(monkeypatch):
    seen = {}

    def fake_describe(image):
        seen["size"] = image.size
        return "a brick wall"

    monkeypatch.setattr(pipeline, "describe", fake_describe)
    photo = Image.new("RGB", (10, 20))
    photo.getexif()[274] = 6  # телефон записал поворот на 90 градусов
    pipeline.run(photo, mode="scene")
    assert seen["size"] == (20, 10)