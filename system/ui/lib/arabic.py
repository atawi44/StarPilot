from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import pyray as rl
from raylib import ffi

_arabic_font: rl.Font | None = None
_font_load_attempted: bool = False

ASSETS_DIR = Path(__file__).resolve().parents[3] / "selfdrive" / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
FONT_PATH = FONTS_DIR / "NotoSansArabic-Bold.ttf"
CODEPOINTS_PATH = FONTS_DIR / "arabic_codepoints.json"


def has_base_arabic(text: str) -> bool:
  if not text or not isinstance(text, str):
    return False
  return any(0x0600 <= ord(c) <= 0x06FF for c in text)


def is_arabic_text(text: str) -> bool:
  if not text or not isinstance(text, str):
    return False
  return any(
    (0x0600 <= ord(c) <= 0x06FF) or
    (0xFB50 <= ord(c) <= 0xFDFF) or
    (0xFE70 <= ord(c) <= 0xFEFF)
    for c in text
  )


@lru_cache(maxsize=1024)
def format_arabic_text(text: str) -> str:
  if not text or not has_base_arabic(text):
    return text
  try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    return get_display(arabic_reshaper.reshape(text))
  except Exception:
    return text


def load_arabic_font() -> rl.Font | None:
  global _arabic_font, _font_load_attempted
  if _arabic_font is not None:
    return _arabic_font
  if _font_load_attempted:
    return None

  _font_load_attempted = True
  if not FONT_PATH.exists() or not CODEPOINTS_PATH.exists():
    return None

  try:
    with CODEPOINTS_PATH.open("r", encoding="utf-8") as f:
      codepoints = json.load(f)

    cp_buf = ffi.new("int[]", codepoints)
    cp_ptr = ffi.cast("int *", cp_buf)

    font = rl.load_font_ex(str(FONT_PATH).encode("utf-8"), 64, cp_ptr, len(codepoints))
    rl.gen_texture_mipmaps(font.texture)
    rl.set_texture_filter(font.texture, rl.TextureFilter.TEXTURE_FILTER_TRILINEAR)
    _arabic_font = font
    return _arabic_font
  except Exception as e:
    print(f"Failed to load Arabic font: {e}")
    return None


def get_arabic_font() -> rl.Font | None:
  global _arabic_font
  if _arabic_font is None:
    return load_arabic_font()
  return _arabic_font
