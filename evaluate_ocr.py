import argparse
import time
from collections import Counter
from pathlib import Path

import jiwer
import pytesseract
from PIL import Image, ImageOps

from scene_reader import config
from scene_reader.ocr import extract_easyocr, extract_tesseract, has_text

PHOTOS = Path("eval_photos")
THRESHOLDS = [1, 2, 3, 5]
CONFIDENCES = [0.0, 0.1, 0.3, 0.5, 0.7]
MAG_RATIOS = [1.0, 1.5, 2.0]


def clean(text):
    return " ".join(text.split()).lower()


def word_scores(refs, hyps):
    found = predicted = expected = 0
    for ref, hyp in zip(refs, hyps):
        ref_words, hyp_words = Counter(ref.split()), Counter(hyp.split())
        found += sum((ref_words & hyp_words).values())
        predicted += sum(hyp_words.values())
        expected += sum(ref_words.values())
    return found / expected, found / predicted if predicted else 0.0


def load_samples(split):
    samples = []
    for path in sorted((PHOTOS / split).iterdir()):
        if path.suffix.lower() not in {".jpg", ".jpeg", ".png"}:
            continue
        img = ImageOps.exif_transpose(Image.open(path))
        ref = clean(path.with_suffix(".txt").read_text(encoding="utf-8-sig"))
        samples.append((path.name, img, ref))
    return samples


def evaluate(samples, name, recognize):
    start = time.perf_counter()
    hyps = [clean(recognize(img)) for _, img, _ in samples]
    seconds = (time.perf_counter() - start) / len(samples)
    pairs = [(ref, hyp) for (_, _, ref), hyp in zip(samples, hyps) if ref]
    refs = [ref for ref, _ in pairs]
    text_hyps = [hyp for _, hyp in pairs]
    recall, precision = word_scores(refs, text_hyps)
    print(f"| {name} | {jiwer.cer(refs, text_hyps):.3f} | {jiwer.wer(refs, text_hyps):.3f} "
          f"| {recall:.3f} | {precision:.3f} | {seconds:.2f} |")
    return hyps


def print_thresholds(samples, hyps):
    print("\n| min_words | верно | пропущен текст | ложный текст |")
    print("|---|---|---|---|")
    for min_words in THRESHOLDS:
        missed = sum(1 for (_, _, ref), hyp in zip(samples, hyps) if ref and not has_text(hyp, min_words=min_words))
        false_text = sum(1 for (_, _, ref), hyp in zip(samples, hyps) if not ref and has_text(hyp, min_words=min_words))
        print(f"| {min_words} | {len(samples) - missed - false_text}/{len(samples)} | {missed} | {false_text} |")


def main():
    parser = argparse.ArgumentParser(description="Сравнивает движки OCR на фото из eval_photos")
    parser.add_argument("--details", action="store_true", help="показать распознанный текст по каждому фото")
    parser.add_argument("--split", choices=["dev", "test"], default="dev", help="набор фото")
    args = parser.parse_args()

    samples = load_samples(args.split)
    with_text = sum(1 for _, _, ref in samples if ref)
    print(f"фото: {len(samples)}, с текстом: {with_text}, без текста: {len(samples) - with_text}\n")

    print("| движок | CER | WER | полнота слов | точность слов | сек/фото |")
    print("|---|---|---|---|---|---|")
    evaluate(samples, "Tesseract без обработки",
             lambda img: pytesseract.image_to_string(img, lang=config.OCR_LANGS))
    tesseract_hyps = evaluate(samples, "Tesseract с обработкой", extract_tesseract)
    easyocr_hyps = {}
    for confidence in CONFIDENCES:
        easyocr_hyps[confidence] = evaluate(samples, f"EasyOCR, уверенность >= {confidence}",
                                            lambda img: extract_easyocr(img, min_confidence=confidence))
    for mag in MAG_RATIOS:
        evaluate(samples, f"EasyOCR, увеличение x{mag}", lambda img: extract_easyocr(img, mag_ratio=mag))

    print("\nTesseract с обработкой:")
    print_thresholds(samples, tesseract_hyps)
    print(f"\nEasyOCR, уверенность >= {config.OCR_MIN_CONFIDENCE}:")
    print_thresholds(samples, [clean(extract_easyocr(img)) for _, img, _ in samples])

    if args.details:
        for (name, _, ref), hyp_t, hyp_e in zip(samples, tesseract_hyps, easyocr_hyps[config.OCR_MIN_CONFIDENCE]):
            print(f"\n{name}\n  эталон:    {ref}\n  Tesseract: {hyp_t}\n  EasyOCR:   {hyp_e}")


if __name__ == "__main__":
    main()
