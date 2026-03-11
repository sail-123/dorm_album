"""
多言語対応ユーティリティ
SYSTEM_ARCHITECTURE.md に定義された4言語をサポート。
"""
import json
import os
import streamlit as st

LANGUAGES = {
    "ja": "日本語",
    "en": "English",
    "id": "Indonesia",
    "my": "ဗမာစာ",
}

_cache: dict = {}


def _load(lang: str) -> dict:
    if lang not in _cache:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "locales", f"{lang}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                _cache[lang] = json.load(f)
        except FileNotFoundError:
            _cache[lang] = {}
    return _cache[lang]


def get_lang() -> str:
    return st.session_state.get("lang", "ja")


def set_lang(lang: str):
    st.session_state.lang = lang
    # ロードキャッシュはそのまま（ファイルは変わらない）


def t(key: str, **kwargs) -> str:
    """
    現在の言語でキーに対応する文字列を返す。
    見つからない場合は日本語にフォールバック、それもなければキーをそのまま返す。
    """
    lang = get_lang()
    data = _load(lang)
    text = data.get(key)
    if text is None:
        ja_data = _load("ja")
        text = ja_data.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text
