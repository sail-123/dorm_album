"""
管理者ページ - UI_SCREEN_SPEC.md #10 / SPEC.md #1 準拠
adminのみアクセス可能。各管理機能へのナビゲーション。
"""
import streamlit as st
from utils.auth import require_admin, get_user, is_app_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_members, get_cleaning_tasks, get_payments,
    get_payment_status, get_items,
)

apply_styles()
require_admin()  # adminでなければ停止
user = get_user()

st.title(f"⚙️ {t('admin_panel')}")
_role_display = "app_admin" if is_app_admin() else "admin"
st.caption(f"🔑 {user['name']} ({t('role')}: {_role_display})")
st.markdown("---")

# ---- データ取得（サマリー用） ----
try:
    members_list = get_members()
    tasks = get_cleaning_tasks()
    payments = get_payments()
    statuses = get_payment_status()
    items = get_items()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

# ---- サマリーカード ----
st.subheader("📊 サマリー")
c1, c2, c3, c4 = st.columns(4)

with c1:
    with st.container(border=True):
        st.metric("👥 " + t("members"), len(members_list))

with c2:
    pending_tasks = sum(1 for t2 in tasks if t2.get("status") == "pending")
    with st.container(border=True):
        st.metric("🧹 " + t("cleaning"), f"{pending_tasks} 未")

with c3:
    with st.container(border=True):
        st.metric("💰 " + t("payments"), len(payments))

with c4:
    need_purchase = sum(1 for i in items if i.get("status") == "need_purchase")
    with st.container(border=True):
        st.metric("📦 " + t("items"), f"{need_purchase} 購入要")

st.markdown("---")

# ---- 管理メニュー ----
st.subheader("🗂 管理メニュー")

menu_items = [
    ("👥", t("members"),       "メンバー情報の追加・編集・削除"),
    ("🧹", t("cleaning"),      "掃除当番の登録・管理"),
    ("💰", t("payments"),      "集金の作成・支払い管理"),
    ("📦", t("items"),         "共用物品の管理"),
    ("📷", t("albums"),        "写真アルバムの管理"),
    ("📢", t("announcements"), "お知らせの投稿・管理"),
    ("💬", t("boards"),        "掲示板の管理"),
    ("📋", t("rules"),         "寮規約の編集"),
]

for icon, page_title, desc in menu_items:
    with st.container(border=True):
        st.markdown(f"#### {icon} {page_title}")
        st.caption(desc)

st.markdown("---")

# ---- 集金未払い状況サマリー ----
st.subheader("💰 集金未払い状況")
if payments:
    for payment in payments:
        pay_id = str(payment.get("id", ""))
        pay_title = payment.get("title", "")
        paid_count = sum(
            1 for s in statuses
            if str(s.get("payment_id", "")) == pay_id
            and str(s.get("paid", "")).lower() == "true"
        )
        total = len(members_list)
        unpaid_count = total - paid_count

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"**{pay_title}**")
        with col2:
            if unpaid_count > 0:
                st.markdown(
                    f'<span class="badge-unpaid">未 {unpaid_count}人</span>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<span class="badge-paid">全員完了</span>',
                    unsafe_allow_html=True,
                )
else:
    st.info(t("no_data"))

st.markdown("---")

# ---- 物品購入必要リスト ----
st.subheader("🛒 購入が必要な物品")
need_items = [i for i in items if i.get("status") == "need_purchase"]
if need_items:
    for item in need_items:
        st.write(f"• **{item.get('name', '')}** （{item.get('quantity', '')}個）  場所: {item.get('location', '')}")
else:
    st.success("購入が必要な物品はありません ✅")
