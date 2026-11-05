import argparse

from PIL import Image

from scene_reader import config
from scene_reader.pipeline import run


def main():
    parser = argparse.ArgumentParser(description="Читает текст или описывает сцену на фото и озвучивает")
    parser.add_argument("image", help="путь к фото")
    parser.add_argument("--mode", choices=["auto", "text", "scene"], default="auto")
    parser.add_argument("--lang", choices=["ru", "en"], default=config.TARGET_LANG)
    parser.add_argument("--out", default="out", help="префикс имён mp3")
    args = parser.parse_args()

    result = run(Image.open(args.image), mode=args.mode, target_lang=args.lang, out_prefix=args.out)
    print(f"[{result.source}] {result.original}")
    print(result.translated)
    print(f"аудио: {result.audio_translated}, {result.audio_original}")


if __name__ == "__main__":
    main()