"""
アルバム - UI_SCREEN_SPEC.md #6 / SPEC.md #6 準拠
全メンバー: 写真投稿・閲覧・いいね・コメント（グリッド表示）
"""
import html as _html
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_albums, add_album, toggle_album_like, delete_album,
    get_album_comments, add_album_comment, get_members,
)
from utils.cloudinary import upload_image

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()
user_id = user["id"]

st.title(f"📷 {t('albums')}")

# ---- データ取得 ----
try:
    albums = get_albums()
    all_comments = get_album_comments()
    members_list = get_members()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

members_map = {str(m["id"]): m["name"] for m in members_list}

# コメントをalbum_idでグループ化
comments_by_album: dict = {}
for c in all_comments:
    aid = str(c.get("album_id", ""))
    comments_by_album.setdefault(aid, []).append(c)

# ---- 写真投稿フォーム ----
with st.expander(f"📸 {t('upload_photo')}"):
    with st.form("upload_form", clear_on_submit=True):
        up_file = st.file_uploader(t("image"), type=["jpg", "jpeg", "png", "webp"])
        up_title = st.text_input(t("title"), placeholder="タイトル")
        up_desc = st.text_area(t("description"), placeholder="説明（任意）", height=80)
        if st.form_submit_button(f"📤 {t('post')}", use_container_width=True):
            if up_file and up_title:
                with st.spinner(t("uploading")):
                    try:
                        image_url = upload_image(up_file)
                        add_album(
                            title=up_title,
                            description=up_desc,
                            image_url=image_url,
                            author_id=user_id,
                        )
                        st.success(t("photo_posted"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")
            else:
                st.warning(t("fill_all_fields"))

st.markdown("---")

# ---- 写真一覧（グリッド表示） ----
if not albums:
    st.info(t("no_photos"))
else:
    # グリッド: 2列
    for i in range(0, len(albums), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(albums):
                break
            album = albums[idx]
            album_id = str(album.get("id", ""))
            with col:
                if album.get("image_url"):
                    st.image(album["image_url"], use_container_width=True)
                st.caption(f"**{album.get('title', '')}**")
                author = members_map.get(str(album.get("author_id", "")), "?")
                st.caption(f"👤 {author}  ·  {album.get('created_at', '')[:10]}")

    # ---- 投稿カード（詳細: いいね・コメント） ----
    st.markdown("---")
    for album in albums:
        album_id = str(album.get("id", ""))
        author = members_map.get(str(album.get("author_id", "")), "?")
        title = album.get("title", "")
        desc = album.get("description", "")
        image_url = album.get("image_url", "")
        created_at = album.get("created_at", "")
        likes: list = album.get("likes", [])
        liked = user_id in likes

        st.markdown('<div class="post-card">', unsafe_allow_html=True)

        # ヘッダー
        st.markdown(
            f"""
            <div class="post-header">
                <span class="post-author">👤 {author}</span>
                <span class="post-time">{created_at}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if image_url:
            st.image(image_url, use_container_width=True)

        if title:
            st.markdown(f'<div class="post-title">{title}</div>', unsafe_allow_html=True)
        if desc:
            desc_html = _html.escape(desc).replace("\n", "<br>")
            st.markdown(f'<div class="post-caption">{desc_html}</div>', unsafe_allow_html=True)

        # いいね・コメント数
        st.markdown('<div class="post-actions">', unsafe_allow_html=True)
        post_comments = comments_by_album.get(album_id, [])
        like_icon = "❤️" if liked else "🤍"
        col_like, col_cmt, col_del = st.columns([2, 2, 1])

        with col_like:
            if st.button(
                f"{like_icon} {len(likes)}",
                key=f"like_{album_id}",
                use_container_width=True,
            ):
                try:
                    toggle_album_like(album_id, user_id)
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('error')}: {e}")

        with col_cmt:
            st.markdown(
                f"<span style='font-size:0.9rem;color:#666;'>💬 {len(post_comments)} {t('comments')}</span>",
                unsafe_allow_html=True,
            )

        with col_del:
            if _is_admin or str(album.get("author_id", "")) == str(user_id):
                if st.button("🗑", key=f"del_album_{album_id}", help=t("delete")):
                    try:
                        delete_album(album_id)
                        st.success(t("photo_deleted"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

        # コメント欄
        with st.expander(t("view_comments")):
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

            new_comment = st.text_input(
                t("enter_comment"),
                key=f"ac_input_{album_id}",
                label_visibility="collapsed",
                placeholder=t("enter_comment"),
            )
            if st.button(t("send"), key=f"ac_send_{album_id}", use_container_width=True):
                if new_comment.strip():
                    try:
                        add_album_comment(album_id, user_id, new_comment.strip())
                        st.success(t("comment_added"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")

        st.markdown("</div>", unsafe_allow_html=True)
