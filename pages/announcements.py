"""
お知らせ - UI_SCREEN_SPEC.md #7 / SPEC.md #7 準拠
admin: 投稿・編集・削除 / member: 閲覧
"""
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_announcements, add_announcement,
    update_announcement, delete_announcement, get_members,
)

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()

st.title(f"📢 {t('announcements')}")

# ---- データ取得 ----
try:
    announcements = get_announcements()
    members_list = get_members()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

members_map = {str(m["id"]): m["name"] for m in members_list}

# ---- 管理者: お知らせ投稿 ----
if _is_admin:
    with st.expander(f"📝 {t('post_announcement')}"):
        with st.form("post_announcement_form"):
            a_title = st.text_input(t("title"), placeholder="今週のお知らせ")
            a_content = st.text_area(t("content"), placeholder="内容を入力してください", height=120)
            if st.form_submit_button(t("post"), use_container_width=True):
                if a_title and a_content:
                    try:
                        add_announcement(
                            title=a_title,
                            content=a_content,
                            author_id=user["id"],
                        )
                        st.success(t("announcement_posted"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")
                else:
                    st.warning(t("fill_all_fields"))

st.markdown("---")

# ---- お知らせ一覧（カード表示） ----
if not announcements:
    st.info(t("no_announcements"))
else:
    for ann in announcements:
        ann_id = str(ann.get("id", ""))
        title = ann.get("title", "")
        content = ann.get("content", "")
        author_id = str(ann.get("author_id", ""))
        created_at = ann.get("created_at", "")
        author_name = members_map.get(author_id, "?")

        with st.container(border=True):
            col_title, col_btn = st.columns([4, 1])
            with col_title:
                st.markdown(f"**📢 {title}**")
                st.caption(f"👤 {author_name}　　📅 {created_at}")
            with col_btn:
                if _is_admin:
                    if st.button("✏️", key=f"edit_ann_{ann_id}", help=t("edit")):
                        st.session_state[f"editing_ann_{ann_id}"] = True

            # 内容表示（expanderで展開）
            with st.expander(t("content")):
                st.markdown(content.replace("\n", "  \n"))

        # 管理者: 編集フォーム
        if _is_admin and st.session_state.get(f"editing_ann_{ann_id}"):
            with st.form(f"edit_ann_form_{ann_id}"):
                st.subheader(t("edit_announcement"))
                e_title = st.text_input(t("title"), value=title)
                e_content = st.text_area(t("content"), value=content, height=120)

                s1, s2, s3 = st.columns(3)
                with s1:
                    if st.form_submit_button(t("save"), use_container_width=True):
                        try:
                            update_announcement(ann_id, {
                                "title": e_title,
                                "content": e_content,
                            })
                            st.success(t("announcement_updated"))
                            del st.session_state[f"editing_ann_{ann_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
                with s2:
                    if st.form_submit_button(t("cancel"), use_container_width=True):
                        del st.session_state[f"editing_ann_{ann_id}"]
                        st.rerun()
                with s3:
                    if st.form_submit_button(f"🗑 {t('delete')}", use_container_width=True):
                        try:
                            delete_announcement(ann_id)
                            st.success(t("announcement_deleted"))
                            del st.session_state[f"editing_ann_{ann_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
