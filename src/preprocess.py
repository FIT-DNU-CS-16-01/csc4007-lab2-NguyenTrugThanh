from __future__ import annotations

import re

import regex as regex_u

URL_RE = re.compile(r"https?://\S+|www\.\S+", flags=re.IGNORECASE)
EMAIL_RE = re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b", flags=re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
MULTI_SPACE_RE = re.compile(r"\s+")
DIGIT_RE = re.compile(r"\b\d+(?:[.,/]\d+)?\b")
PUNCT_RE = re.compile(r"([!?.,;:()\[\]{}\"'\-_/])")


def gentle_clean_text(text: str) -> str:
    """Tiền xử lý nhẹ nhàng - chỉ loại bỏ HTML tags và làm sạch whitespace.
    
    Chiến lược này giữ lại hầu hết các ký tự gốc để tránh mất tín hiệu cảm xúc.
    - Loại bỏ HTML tags
    - Chuyển thành chữ thường
    - Làm sạch whitespace
    - Giữ lại dấu câu và số
    """
    if text is None:
        return ""

    t = str(text).strip()
    t = t.replace("\u00a0", " ")
    t = HTML_TAG_RE.sub(" ", t)
    t = regex_u.sub(r"\p{C}+", " ", t)
    t = t.lower()
    t = MULTI_SPACE_RE.sub(" ", t).strip()
    return t


def aggressive_clean_text(text: str) -> str:
    """Tiền xử lý tích cực - loại bỏ dấu câu, số và URLs.
    
    Chiến lược này tập trung vào từ vựng chính để giảm noise.
    - Loại bỏ HTML tags
    - Loại bỏ URLs và emails
    - Thay thế số bằng <NUM>
    - Loại bỏ dấu câu
    - Chuyển thành chữ thường
    """
    if text is None:
        return ""

    t = str(text).strip()
    t = t.replace("\u00a0", " ")
    t = HTML_TAG_RE.sub(" ", t)
    t = regex_u.sub(r"\p{C}+", " ", t)
    t = URL_RE.sub(" <URL> ", t)
    t = EMAIL_RE.sub(" <EMAIL> ", t)
    t = DIGIT_RE.sub(" <NUM> ", t)
    t = t.lower()
    t = PUNCT_RE.sub(" ", t)
    t = MULTI_SPACE_RE.sub(" ", t).strip()
    return t


def basic_clean_text(
    text: str,
    lowercase: bool = True,
    replace_url: bool = True,
    replace_email: bool = True,
    replace_number: bool = False,
    keep_punct: bool = True,
) -> str:
    """Tiền xử lý mức vừa phải cho IMDB.

    Chủ đích của Lab 2 là để sinh viên so sánh pipeline,
    nên hàm này chỉ làm sạch vừa phải thay vì “dọn quá tay”.
    """
    if text is None:
        return ""

    t = str(text).strip()
    t = t.replace("\u00a0", " ")
    t = HTML_TAG_RE.sub(" ", t)
    t = regex_u.sub(r"\p{C}+", " ", t)

    if replace_url:
        t = URL_RE.sub(" <URL> ", t)
    if replace_email:
        t = EMAIL_RE.sub(" <EMAIL> ", t)
    if replace_number:
        t = DIGIT_RE.sub(" <NUM> ", t)
    if lowercase:
        t = t.lower()

    if keep_punct:
        t = PUNCT_RE.sub(r" \1 ", t)
    else:
        t = PUNCT_RE.sub(" ", t)

    t = MULTI_SPACE_RE.sub(" ", t).strip()
    return t
