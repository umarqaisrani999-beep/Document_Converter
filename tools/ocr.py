"""
OCR Logic Module
=================
Extracts text from image files using EasyOCR (preferred — zero system
dependencies) with a graceful fallback to pytesseract if EasyOCR is
unavailable. Both engines support common image formats (PNG, JPEG, BMP,
TIFF, WebP).

Public API
----------
extract_text_from_image(image_path, lang="en", progress_cb=None) -> str
    Returns the full extracted text as a single string, with paragraphs
    separated by blank lines.  Raises RuntimeError on total failure.

get_supported_languages() -> list[str]
    Returns a list of language codes supported by the active engine.
"""

from __future__ import annotations
import os


# ---------------------------------------------------------------------------
# Engine detection (done once at import time so repeated calls are cheap)
# ---------------------------------------------------------------------------
_ENGINE: str | None = None          # "easyocr" | "tesseract" | None
_READER = None                      # cached easyocr.Reader instance


def _detect_engine() -> str:
    global _ENGINE
    if _ENGINE is not None:
        return _ENGINE

    try:
        import easyocr  # noqa: F401
        _ENGINE = "easyocr"
    except ImportError:
        try:
            import pytesseract  # noqa: F401
            pytesseract.get_tesseract_version()   # raises if binary missing
            _ENGINE = "tesseract"
        except Exception:
            _ENGINE = "none"

    return _ENGINE


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------
def get_supported_languages() -> list[str]:
    engine = _detect_engine()
    if engine == "easyocr":
        return ["en", "ch_sim", "ch_tra", "fr", "de", "es", "ar",
                "hi", "ja", "ko", "pt", "ru", "it", "tr"]
    if engine == "tesseract":
        try:
            import pytesseract
            return pytesseract.get_languages(config="")
        except Exception:
            return ["eng"]
    return ["en"]


# ---------------------------------------------------------------------------
# Core extraction
# ---------------------------------------------------------------------------
def extract_text_from_image(
    image_path: str,
    lang: str = "en",
    progress_cb=None,
) -> str:
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    engine = _detect_engine()

    if engine == "easyocr":
        return _extract_easyocr(image_path, lang, progress_cb)
    elif engine == "tesseract":
        return _extract_tesseract(image_path, lang, progress_cb)
    else:
        raise RuntimeError(
            "No OCR engine found.\n\n"
            "Install one of:\n"
            "  pip install easyocr\n"
            "  pip install pytesseract   (also needs Tesseract binary)"
        )


# ---------------------------------------------------------------------------
# EasyOCR engine
# ---------------------------------------------------------------------------
def _extract_easyocr(image_path: str, lang: str, progress_cb) -> str:
    global _READER
    import easyocr

    if progress_cb:
        progress_cb(5, "Loading OCR model (first run downloads ~100 MB)…")

    langs = [lang] if lang == "en" else [lang, "en"]
    langs = list(dict.fromkeys(langs))

    reader_key = tuple(sorted(langs))
    if _READER is None or getattr(_READER, "_langs_key", None) != reader_key:
        if progress_cb:
            progress_cb(15, "Initialising neural network…")
        _READER = easyocr.Reader(langs, gpu=False, verbose=False)
        _READER._langs_key = reader_key

    if progress_cb:
        progress_cb(40, "Running text detection…")

    results = _READER.readtext(image_path, detail=1, paragraph=True)

    if progress_cb:
        progress_cb(85, "Assembling text…")

    lines: list[str] = []
    for item in results:
        text = item[1].strip()
        if text:
            lines.append(text)

    if progress_cb:
        progress_cb(100, "OCR complete.")

    return "\n\n".join(lines) if lines else "(No text detected in this image.)"


# ---------------------------------------------------------------------------
# Tesseract engine (fallback)
# ---------------------------------------------------------------------------
_TESS_LANG_MAP = {
    "en": "eng", "fr": "fra", "de": "deu", "es": "spa",
    "it": "ita", "pt": "por", "ru": "rus", "ar": "ara",
    "hi": "hin", "ja": "jpn", "ko": "kor", "tr": "tur",
    "ch_sim": "chi_sim", "ch_tra": "chi_tra",
}


def _extract_tesseract(image_path: str, lang: str, progress_cb) -> str:
    import pytesseract
    from PIL import Image

    tess_lang = _TESS_LANG_MAP.get(lang, lang)

    if progress_cb:
        progress_cb(20, f"Running Tesseract OCR (lang={tess_lang})…")

    img = Image.open(image_path)
    text: str = pytesseract.image_to_string(img, lang=tess_lang)

    if progress_cb:
        progress_cb(100, "OCR complete.")

    return text.strip() if text.strip() else "(No text detected in this image.)"