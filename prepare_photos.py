"""Готовит фото для публикации: поворачивает по EXIF, уменьшает и удаляет метаданные (в том числе GPS).

Запускать один раз после копирования фото в eval_photos/dev и eval_photos/test.
Перезаписывает файлы, поэтому оригиналы сохраните отдельно.
"""
from pathlib import Path
import sys
from PIL import Image, ImageOps

PHOTOS = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("eval_photos")
MAX_SIDE = 2048

count = 0
for path in sorted(PHOTOS.rglob("*")):
    if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
        continue
    img = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    path.unlink()  # фото уже в памяти; удаляем, чтобы IMG.JPG и IMG.jpg не стали двумя файлами
    out = path.with_suffix(".jpg")
    img.save(out, "JPEG", quality=90)  # без exif=...: координаты и данные телефона не сохраняются
    label = out.with_suffix(".txt")
    if not label.exists():
        label.write_text("", encoding="utf-8")
    count += 1

print(f"Готово: {count} фото")
