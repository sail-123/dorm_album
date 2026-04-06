"""
ダッシュボード - UI_SCREEN_SPEC.md #1 準拠
ログイン後のトップページ。今日の掃除当番・未払い集金・最新情報を表示。
"""
import streamlit as st
from utils.auth import require_auth, get_user
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_cleaning_tasks, get_members, get_payments,
    get_payment_status, get_announcements, get_albums, get_boards,
)
from datetime import datetime, timezone, timedelta

apply_styles()
require_auth()
user = get_user()

st.title(f"🏠 {t('dashboard')}")
st.caption(f"{t('welcome')}, **{user['name']}** さん")
st.markdown("---")

# ---- データ取得 ----
try:
    with st.spinner(t("loading")):
        tasks = get_cleaning_tasks()
        members_list = get_members()
        payments = get_payments()
        statuses = get_payment_status()
        announcements = get_announcements()
        albums = get_albums()
        boards = get_boards()
    members_map = {str(m["id"]): m["name"] for m in members_list}
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

JST = timezone(timedelta(hours=9))
today = str(datetime.now(JST).date())
user_id = user["id"]

# ---- Row 1: 掃除当番 / 未払い集金 ----
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown(f"#### 🧹 {t('today_cleaning')}")
        today_tasks = [
            task for task in tasks
            if today in (task.get("dates") if isinstance(task.get("dates"), list) else [])
            and task.get("status") != "done"
        ]
        if today_tasks:
            for task in today_tasks[:3]:
                name = members_map.get(str(task.get("member_id", "")), "?")
                st.caption(f"👤 {name}")
        else:
            st.success(t("no_cleaning_today"))

with col2:
    with st.container(border=True):
        st.markdown(f"#### 💰 {t('unpaid_payments')}")
        paid_ids = {
            str(s["payment_id"])
            for s in statuses
            if str(s.get("member_id", "")) == str(user_id)
            and str(s.get("paid", "")).lower() == "true"
        }
        unpaid = [p for p in payments if str(p.get("id", "")) not in paid_ids]
        if unpaid:
            for p in unpaid[:3]:
                st.write(f"• {p.get('title', '')}")
                st.caption(f"¥{p.get('amount', '')} 　期限: {p.get('due_date', '')}")
        else:
            st.success(t("no_unpaid_payments"))

# ---- お知らせ ----
with st.container(border=True):
    st.markdown(f"#### 📢 {t('latest_news')}")
    if announcements:
        for a in announcements[:3]:
            st.markdown(
                f'<div class="announce-card"><b>{a.get("title","")}</b>'
                f'<br><small style="color:#888">{a.get("created_at","")}</small></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info(t("no_announcements"))

# ---- 最新アルバム ----
with st.container(border=True):
    st.markdown(f"#### 📷 {t('latest_photos')}")
    if albums:
        cols = st.columns(3)
        for i, album in enumerate(albums[:3]):
            with cols[i]:
                if album.get("image_url"):
                    st.image(album["image_url"], use_container_width=True)
                st.caption(album.get("title", ""))
    else:
        st.info(t("no_photos"))

# ---- 最近の掲示板投稿 ----
with st.container(border=True):
    st.markdown(f"#### 💬 {t('recent_posts')}")
    if boards:
        for post in boards[:3]:
            author = members_map.get(str(post.get("author_id", "")), "?")
            st.write(f"**{post.get('title', '')}**")
            st.caption(f"{author}  ·  {post.get('created_at', '')}")
            st.markdown("---")
    else:
        st.info(t("no_posts"))
