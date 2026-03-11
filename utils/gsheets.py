"""
Google Sheets CRUD ユーティリティ
DATA_SCHEMA.md に定義された全シートの操作を提供する。
"""
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# 各シートのヘッダー定義（DATA_SCHEMA.md 準拠）
SHEET_HEADERS = {
    "members": ["id", "name", "room", "phone", "email", "role", "join_date", "password", "gender", "nationality"],
    "cleaning_tasks": ["id", "member_id", "location", "dates", "status"],
    "payments": ["id", "title", "amount", "due_date", "description"],
    "payment_status": ["id", "payment_id", "member_id", "paid"],
    "items": ["id", "name", "quantity", "location", "status"],
    "albums": ["id", "title", "description", "image_url", "author_id", "created_at", "likes"],
    "album_comments": ["id", "album_id", "author_id", "content", "created_at"],
    "announcements": ["id", "title", "content", "author_id", "created_at"],
    "boards": ["id", "title", "content", "author_id", "created_at"],
    "comments": ["id", "board_id", "author_id", "content", "created_at"],
    "rules": ["id", "title", "content", "updated_at"],
}


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


def _ensure_sheet(name: str) -> gspread.Worksheet:
    """シートが存在しなければ作成してヘッダーを設定する。"""
    ss = _get_spreadsheet()
    headers = SHEET_HEADERS.get(name, ["id"])
    try:
        ws = ss.worksheet(name)
        # ヘッダーが空なら初期化
        if not ws.row_values(1):
            ws.append_row(headers)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(name, rows=2000, cols=len(headers))
        ws.append_row(headers)
    return ws


def _new_id() -> str:
    return str(uuid.uuid4())[:8]


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _records_to_list(ws: gspread.Worksheet) -> list:
    return ws.get_all_records()


def _find_row(ws: gspread.Worksheet, id_value: str) -> tuple[int, dict | None]:
    """IDに一致する行番号（2始まり）とレコードを返す。見つからなければ (-1, None)。"""
    records = ws.get_all_records()
    for i, record in enumerate(records):
        if str(record.get("id", "")) == str(id_value):
            return i + 2, record
    return -1, None


def _update_row(ws: gspread.Worksheet, row_num: int, data: dict):
    """指定行のデータを更新する。"""
    headers = ws.row_values(1)
    for key, value in data.items():
        if key in headers:
            col = headers.index(key) + 1
            ws.update_cell(row_num, col, value)


def _append_record(ws: gspread.Worksheet, data: dict) -> str:
    """レコードを追加し、生成したIDを返す。data に id が設定済みの場合はそれを使用する。"""
    record_id = data.get("id") or _new_id()
    data["id"] = record_id
    headers = ws.row_values(1)
    row = [str(data.get(h, "")) for h in headers]
    ws.append_row(row)
    st.cache_data.clear()
    return record_id


# ===========================================================================
# members
# ===========================================================================

@st.cache_data(ttl=30)
def get_members() -> list:
    ws = _ensure_sheet("members")
    records = ws.get_all_records()
    # password フィールドは返さない（ログイン処理内でのみ参照）
    return records


def get_members_with_password() -> list:
    """認証用: passwordを含む全レコードを返す（キャッシュなし）。"""
    ws = _ensure_sheet("members")
    return ws.get_all_records()


def add_member(name: str, room: str, phone: str, email: str,
               role: str, join_date: str, password_hash: str,
               user_id: str = "", gender: str = "", nationality: str = "") -> str:
    ws = _ensure_sheet("members")
    data = {
        "name": name, "room": room, "phone": phone, "email": email,
        "role": role, "join_date": join_date, "password": password_hash,
        "gender": gender, "nationality": nationality,
    }
    if user_id:
        data["id"] = user_id
    record_id = _append_record(ws, data)
    return record_id


def update_member(member_id: str, data: dict):
    ws = _ensure_sheet("members")
    row_num, _ = _find_row(ws, member_id)
    if row_num > 0:
        _update_row(ws, row_num, data)
        st.cache_data.clear()


def delete_member(member_id: str):
    ws = _ensure_sheet("members")
    row_num, _ = _find_row(ws, member_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# cleaning_tasks
# ===========================================================================

@st.cache_data(ttl=30)
def get_cleaning_tasks() -> list:
    ws = _ensure_sheet("cleaning_tasks")
    records = ws.get_all_records()
    for r in records:
        raw = r.get("dates", "")
        try:
            r["dates"] = json.loads(raw) if raw else []
        except Exception:
            r["dates"] = [d.strip() for d in str(raw).split(",") if d.strip()]
    return records


def add_cleaning_task(member_id: str, location: str, dates: str) -> str:
    ws = _ensure_sheet("cleaning_tasks")
    data = {
        "member_id": member_id, "location": location,
        "dates": dates, "status": "pending",
    }
    return _append_record(ws, data)


def update_cleaning_task(task_id: str, data: dict):
    ws = _ensure_sheet("cleaning_tasks")
    row_num, _ = _find_row(ws, task_id)
    if row_num > 0:
        _update_row(ws, row_num, data)
        st.cache_data.clear()


def complete_cleaning_task(task_id: str):
    update_cleaning_task(task_id, {"status": "done"})


def delete_cleaning_task(task_id: str):
    ws = _ensure_sheet("cleaning_tasks")
    row_num, _ = _find_row(ws, task_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# payments
# ===========================================================================

@st.cache_data(ttl=30)
def get_payments() -> list:
    ws = _ensure_sheet("payments")
    return ws.get_all_records()


def add_payment(title: str, amount: str, due_date: str, description: str) -> str:
    ws = _ensure_sheet("payments")
    data = {"title": title, "amount": amount, "due_date": due_date, "description": description}
    return _append_record(ws, data)


def update_payment(payment_id: str, data: dict):
    ws = _ensure_sheet("payments")
    row_num, _ = _find_row(ws, payment_id)
    if row_num > 0:
        _update_row(ws, row_num, data)
        st.cache_data.clear()


def delete_payment(payment_id: str):
    ws = _ensure_sheet("payments")
    row_num, _ = _find_row(ws, payment_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# payment_status
# ===========================================================================

@st.cache_data(ttl=30)
def get_payment_status() -> list:
    ws = _ensure_sheet("payment_status")
    return ws.get_all_records()


def set_payment_status(payment_id: str, member_id: str, paid: bool):
    ws = _ensure_sheet("payment_status")
    records = ws.get_all_records()
    for i, record in enumerate(records):
        if (str(record.get("payment_id")) == str(payment_id) and
                str(record.get("member_id")) == str(member_id)):
            ws.update_cell(i + 2, 4, str(paid).lower())
            st.cache_data.clear()
            return
    # 存在しなければ追加
    data = {"payment_id": payment_id, "member_id": member_id, "paid": str(paid).lower()}
    _append_record(ws, data)


# ===========================================================================
# items
# ===========================================================================

@st.cache_data(ttl=30)
def get_items() -> list:
    ws = _ensure_sheet("items")
    return ws.get_all_records()


def add_item(name: str, quantity: str, location: str, status: str) -> str:
    ws = _ensure_sheet("items")
    data = {"name": name, "quantity": quantity, "location": location, "status": status}
    return _append_record(ws, data)


def update_item(item_id: str, data: dict):
    ws = _ensure_sheet("items")
    row_num, _ = _find_row(ws, item_id)
    if row_num > 0:
        _update_row(ws, row_num, data)
        st.cache_data.clear()


def delete_item(item_id: str):
    ws = _ensure_sheet("items")
    row_num, _ = _find_row(ws, item_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# albums
# ===========================================================================

@st.cache_data(ttl=30)
def get_albums() -> list:
    ws = _ensure_sheet("albums")
    records = ws.get_all_records()
    for r in records:
        try:
            r["likes"] = json.loads(r.get("likes", "[]") or "[]")
        except Exception:
            r["likes"] = []
    return list(reversed(records))


def add_album(title: str, description: str, image_url: str, author_id: str) -> str:
    ws = _ensure_sheet("albums")
    data = {
        "title": title, "description": description, "image_url": image_url,
        "author_id": author_id, "created_at": _now(), "likes": "[]",
    }
    return _append_record(ws, data)


def toggle_album_like(album_id: str, user_id: str) -> list:
    ws = _ensure_sheet("albums")
    records = ws.get_all_records()
    headers = ws.row_values(1)
    likes_col = headers.index("likes") + 1 if "likes" in headers else None
    for i, record in enumerate(records):
        if str(record.get("id", "")) == str(album_id):
            try:
                likes = json.loads(record.get("likes", "[]") or "[]")
            except Exception:
                likes = []
            if user_id in likes:
                likes.remove(user_id)
            else:
                likes.append(user_id)
            if likes_col:
                ws.update_cell(i + 2, likes_col, json.dumps(likes, ensure_ascii=False))
            st.cache_data.clear()
            return likes
    return []


def delete_album(album_id: str):
    ws = _ensure_sheet("albums")
    row_num, _ = _find_row(ws, album_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# album_comments
# ===========================================================================

@st.cache_data(ttl=30)
def get_album_comments() -> list:
    ws = _ensure_sheet("album_comments")
    return ws.get_all_records()


def add_album_comment(album_id: str, author_id: str, content: str) -> str:
    ws = _ensure_sheet("album_comments")
    data = {"album_id": album_id, "author_id": author_id,
            "content": content, "created_at": _now()}
    return _append_record(ws, data)


# ===========================================================================
# announcements
# ===========================================================================

@st.cache_data(ttl=30)
def get_announcements() -> list:
    ws = _ensure_sheet("announcements")
    return list(reversed(ws.get_all_records()))


def add_announcement(title: str, content: str, author_id: str) -> str:
    ws = _ensure_sheet("announcements")
    data = {"title": title, "content": content,
            "author_id": author_id, "created_at": _now()}
    return _append_record(ws, data)


def update_announcement(announcement_id: str, data: dict):
    ws = _ensure_sheet("announcements")
    row_num, _ = _find_row(ws, announcement_id)
    if row_num > 0:
        _update_row(ws, row_num, data)
        st.cache_data.clear()


def delete_announcement(announcement_id: str):
    ws = _ensure_sheet("announcements")
    row_num, _ = _find_row(ws, announcement_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# boards
# ===========================================================================

@st.cache_data(ttl=30)
def get_boards() -> list:
    ws = _ensure_sheet("boards")
    return list(reversed(ws.get_all_records()))


def add_board(title: str, content: str, author_id: str) -> str:
    ws = _ensure_sheet("boards")
    data = {"title": title, "content": content,
            "author_id": author_id, "created_at": _now()}
    return _append_record(ws, data)


def delete_board(board_id: str):
    ws = _ensure_sheet("boards")
    row_num, _ = _find_row(ws, board_id)
    if row_num > 0:
        ws.delete_rows(row_num)
        st.cache_data.clear()


# ===========================================================================
# comments (掲示板コメント)
# ===========================================================================

@st.cache_data(ttl=30)
def get_comments() -> list:
    ws = _ensure_sheet("comments")
    return ws.get_all_records()


def add_comment(board_id: str, author_id: str, content: str) -> str:
    ws = _ensure_sheet("comments")
    data = {"board_id": board_id, "author_id": author_id,
            "content": content, "created_at": _now()}
    return _append_record(ws, data)


# ===========================================================================
# rules
# ===========================================================================

@st.cache_data(ttl=60)
def get_rules() -> list:
    ws = _ensure_sheet("rules")
    return ws.get_all_records()


def save_rule(title: str, content: str):
    """規約を上書き保存（最初の1件のみ管理）。"""
    ws = _ensure_sheet("rules")
    records = ws.get_all_records()
    now = _now()
    if records:
        row_num = 2  # 最初のデータ行
        _update_row(ws, row_num, {"title": title, "content": content, "updated_at": now})
    else:
        data = {"title": title, "content": content, "updated_at": now}
        _append_record(ws, data)
    st.cache_data.clear()
