import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json
import os
from datetime import datetime
import uuid
from dotenv import load_dotenv

load_dotenv()

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _get_creds():
    creds_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        creds_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
    creds_file = os.getenv("GOOGLE_CREDENTIALS_FILE", "credentials.json")
    if os.path.exists(creds_file):
        return ServiceAccountCredentials.from_json_keyfile_name(creds_file, SCOPE)
    raise ValueError(
        "Google認証情報が見つかりません。GOOGLE_CREDENTIALS_JSON または credentials.json を設定してください"
    )


@st.cache_resource
def _get_client():
    return gspread.authorize(_get_creds())


def _get_spreadsheet():
    client = _get_client()
    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_id:
        raise ValueError("SPREADSHEET_ID が環境変数に設定されていません")
    return client.open_by_key(spreadsheet_id)


def _ensure_sheet(name: str, headers: list):
    ss = _get_spreadsheet()
    try:
        ws = ss.worksheet(name)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(name, rows=2000, cols=len(headers))
        ws.append_row(headers)
    return ws


def _posts_sheet():
    return _ensure_sheet(
        "posts",
        ["post_id", "timestamp", "author", "title", "caption", "image_url", "likes"],
    )


def _comments_sheet():
    return _ensure_sheet(
        "comments",
        ["comment_id", "post_id", "author", "comment", "timestamp"],
    )


def save_post(author: str, title: str, caption: str, image_url: str) -> str:
    ws = _posts_sheet()
    post_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.append_row([post_id, timestamp, author, title, caption, image_url, "[]"])
    st.cache_data.clear()
    return post_id


@st.cache_data(ttl=30)
def get_posts() -> list:
    ws = _posts_sheet()
    records = ws.get_all_records()
    for r in records:
        try:
            r["likes"] = json.loads(r.get("likes", "[]") or "[]")
        except Exception:
            r["likes"] = []
    return list(reversed(records))


def toggle_like(post_id: str, user_name: str) -> list:
    ws = _posts_sheet()
    records = ws.get_all_records()
    for i, row in enumerate(records):
        if str(row.get("post_id", "")) == str(post_id):
            row_num = i + 2  # 1-indexed + header row
            try:
                likes = json.loads(row.get("likes", "[]") or "[]")
            except Exception:
                likes = []
            if user_name in likes:
                likes.remove(user_name)
            else:
                likes.append(user_name)
            ws.update_cell(row_num, 7, json.dumps(likes, ensure_ascii=False))
            st.cache_data.clear()
            return likes
    return []


def add_comment(post_id: str, author: str, comment: str):
    ws = _comments_sheet()
    comment_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    ws.append_row([comment_id, post_id, author, comment, timestamp])
    st.cache_data.clear()


@st.cache_data(ttl=30)
def get_all_comments() -> list:
    ws = _comments_sheet()
    return ws.get_all_records()
