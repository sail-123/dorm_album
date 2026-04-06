"""
認証ユーティリティ
PERMISSION_SPEC.md に準拠したログイン・権限管理。
"""
import hashlib
import streamlit as st
from utils.gsheets import get_members_with_password


def hash_password(password: str) -> str:
    """SHA-256でパスワードをハッシュ化する。"""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def login_user(user_id: str, password: str) -> bool:
    """
    ユーザIDとパスワードで認証を行う。
    成功時は session_state.user に情報を保存して True を返す。
    """
    try:
        members = get_members_with_password()
        hashed = hash_password(password)
        for member in members:
            if (str(member.get("id", "")).strip() == user_id.strip() and
                    str(member.get("password", "")).strip() == hashed):
                st.session_state.user = {
                    "id": str(member.get("id", "")),
                    "name": str(member.get("name", "")),
                    "email": str(member.get("email", "")),
                    "role": str(member.get("role", "member")),
                }
                return True
        return False
    except Exception as e:
        st.error(f"ログインエラー: {e}")
        return False


def is_logged_in() -> bool:
    return "user" in st.session_state and bool(st.session_state.get("user"))


def get_user() -> dict:
    return st.session_state.get("user", {})


def is_admin() -> bool:
    """adminまたはapp_adminの場合にTrueを返す。"""
    return get_user().get("role") in ("admin", "app_admin")


def is_app_admin() -> bool:
    """app_admin（アプリケーション管理者）の場合にTrueを返す。"""
    return get_user().get("role") == "app_admin"


def require_auth():
    """未ログインの場合は処理を停止する。各ページの先頭で呼び出す。"""
    if not is_logged_in():
        st.warning("ログインが必要です。トップページからログインしてください。")
        st.stop()


def require_admin():
    """管理者でない場合は処理を停止する。"""
    require_auth()
    if not is_admin():
        st.error("この機能は管理者のみ利用可能です。")
        st.stop()


def require_app_admin():
    """アプリケーション管理者でない場合は処理を停止する。"""
    require_auth()
    if not is_app_admin():
        st.error("この機能はアプリケーション管理者のみ利用可能です。")
        st.stop()


def logout():
    """セッションをクリアしてログアウトする。"""
    keys = list(st.session_state.keys())
    for key in keys:
        del st.session_state[key]
