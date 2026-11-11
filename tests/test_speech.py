import pytest

from scene_reader import speech


@pytest.fixture
def saved(monkeypatch):
    calls = []

    class FakeTTS:
        def __init__(self, text, lang):
            self.text = text
            self.lang = lang

        def save(self, path):
            calls.append((self.text, self.lang, path))

    monkeypatch.setattr(speech, "gTTS", FakeTTS)
    return calls


def test_two_tracks_when_translated(saved):
    paths = speech.speak("стена", "wall", "ru")
    assert paths == ("out_translated.mp3", "out_original.mp3")
    assert saved == [
        ("стена", "ru", "out_translated.mp3"),
        ("wall", "en", "out_original.mp3"),
    ]


def test_one_track_when_same_language(saved):
    paths = speech.speak("стена", "стена", "ru")
    assert paths == ("out_translated.mp3", None)
    assert len(saved) == 1


def test_failed_tts_keeps_result(monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("нет интернета")

    monkeypatch.setattr(speech, "gTTS", fail)
    assert speech.speak("стена", "стена", "ru") == (None, None)