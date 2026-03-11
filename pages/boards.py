"""
掲示板 - UI_SCREEN_SPEC.md #8 / SPEC.md #8 準拠
全メンバー: 投稿・コメント / admin: 削除
"""
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_boards, add_board, delete_board,
    get_comments, add_comment, get_members,
)

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()
user_id = user["id"]

st.title(f"💬 {t('boards')}")

# ---- データ取得 ----
try:
    posts = get_boards()
    all_comments = get_comments()
    members_list = get_members()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

members_map = {str(m["id"]): m["name"] for m in members_list}

# コメントをboard_idでグループ化
comments_by_post: dict = {}
for c in all_comments:
    pid = str(c.get("board_id", ""))
    comments_by_post.setdefault(pid, []).append(c)

# ---- 投稿作成フォーム ----
with st.expander(f"✏️ {t('create_post')}"):
    with st.form("create_post_form", clear_on_submit=True):
        b_title = st.text_input(t("title"), placeholder="タイトルを入力")
        b_content = st.text_area(t("content"), placeholder="内容を入力してください", height=100)
        if st.form_submit_button(f"📤 {t('post')}", use_container_width=True):
            if b_title and b_content:
                try:
                    add_board(
                        title=b_title,
                        content=b_content,
                        author_id=user_id,
                    )
                    st.success(t("post_created"))
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('error')}: {e}")
            else:
                st.warning(t("fill_all_fields"))

st.markdown("---")

# ---- 投稿一覧（スレッド形式） ----
if not posts:
    st.info(t("no_posts"))
else:
    for post in posts:
        post_id = str(post.get("id", ""))
        title = post.get("title", "")
        content = post.get("content", "")
        author_id = str(post.get("author_id", ""))
        created_at = post.get("created_at", "")
        author_name = members_map.get(author_id, "?")
        post_comments = comments_by_post.get(post_id, [])

        with st.container(border=True):
            col_info, col_del = st.columns([5, 1])
            with col_info:
                st.markdown(f"**{title}**")
                st.markdown(content.replace("\n", "  \n"))
                st.caption(f"👤 {author_name}　　📅 {created_at}　　💬 {len(post_comments)}")
            with col_del:
                if _is_admin or author_id == str(user_id):
                    if st.button("🗑", key=f"del_post_{post_id}", help=t("delete")):
                        try:
                            delete_board(post_id)
                            st.success(t("post_deleted"))
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")

        # コメントスレッド
        with st.expander(f"💬 {t('view_comments')} ({len(post_comments)})"):
            if post_comments:
                for c in post_comments:
                    c_author = members_map.get(str(c.get("author_id", "")), "?")
                    st.markdown(
                        f"""
                        <div class="comment-item">
                            <span class="comment-author">{c_author}</span>
                            <span class="comment-text">{c.get('content', '')}</span>
                            <span class="comment-time">{c.get('created_at', '')}</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
            else:
                st.caption(t("no_comments"))

            # コメント送信
            new_comment = st.text_input(
                t("write_comment"),
                key=f"bc_input_{post_id}",
                label_visibility="collapsed",
                placeholder=t("enter_comment"),
            )
            if st.button(t("send"), key=f"bc_send_{post_id}", use_container_width=True):
                if new_comment.strip():
                    try:
                        add_comment(post_id, user_id, new_comment.strip())
                        st.success(t("comment_added"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")
                else:
                    st.warning(t("enter_comment"))
