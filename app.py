import tempfile
from pathlib import Path

import gradio as gr

from scene_reader import config
from scene_reader.pipeline import run


def process(image, mode, lang):
    out_prefix = str(Path(tempfile.mkdtemp()) / "out")
    result = run(image, mode, lang, out_prefix=out_prefix)
    return result.original, result.translated, result.audio_translated, result.audio_original


demo = gr.Interface(
    fn=process,
    inputs=[
        gr.Image(type="pil", label="Фото"),
        gr.Radio(["auto", "text", "scene"], value="auto", label="Режим"),
        gr.Radio(["ru", "en"], value=config.TARGET_LANG, label="Язык"),
    ],
    outputs=[
        gr.Textbox(label="Оригинал"),
        gr.Textbox(label="Перевод"),
        gr.Audio(type="filepath", label="Озвучка перевода"),
        gr.Audio(type="filepath", label="Озвучка оригинала"),
    ],
    title="scene-reader",
)

if __name__ == "__main__":
    demo.launch()