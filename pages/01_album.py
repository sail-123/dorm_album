import streamlit as st
from utils.sheets import get_posts, get_all_comments, toggle_like, add_comment
from utils.styles import apply_styles, user_name_selector

st.set_page_config(
    page_title="アルバム | 寮アルバム",
    page_icon="📷",
    layout="centered",
)

apply_styles()
user_name = user_name_selector()

st.title("📷 アルバム")

if not user_name:
    st.warning("👈 サイドバーで名前を入力するといいねやコメントができます")

# ---- データ取得 ----
try:
    with st.spinner("読み込み中..."):
        posts = get_posts()
        all_comments = get_all_comments()
except Exception as e:
    st.error(f"データの読み込みに失敗しました: {e}")
    st.stop()

if not posts:
    st.info("まだ投稿がありません。写真を投稿してみましょう！")
    st.stop()

# コメントをpost_idでグループ化
comments_by_post: dict = {}
for c in all_comments:
    pid = str(c.get("post_id", ""))
    comments_by_post.setdefault(pid, []).append(c)

# ---- 投稿カード ----
for post in posts:
    post_id   = str(post.get("post_id", ""))
    author    = post.get("author", "不明")
    title     = post.get("title", "")
    caption   = post.get("caption", "")
    image_url = post.get("image_url", "")
    timestamp = post.get("timestamp", "")
    likes: list = post.get("likes", [])
    liked = user_name in likes if user_name else False

    st.markdown('<div class="post-card">', unsafe_allow_html=True)

    # ヘッダー（投稿者・日時）
    st.markdown(
        f"""
        <div class="post-header">
            <span class="post-author">👤 {author}</span>
            <span class="post-time">{timestamp}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 画像
    if image_url:
        st.image(image_url, use_container_width=True)

    # タイトル・キャプション
    if title:
        st.markdown(f'<div class="post-title">{title}</div>', unsafe_allow_html=True)
    if caption:
        st.markdown(f'<div class="post-caption">{caption}</div>', unsafe_allow_html=True)

    # ---- いいね & コメント ----
    st.markdown('<div class="post-actions">', unsafe_allow_html=True)

    post_comments = comments_by_post.get(post_id, [])
    like_icon = "❤️" if liked else "🤍"
    col_like, col_comment = st.columns([1, 2])

    with col_like:
        if st.button(
            f"{like_icon} {len(likes)}",
            key=f"like_{post_id}",
            use_container_width=True,
            disabled=not bool(user_name),
        ):
            with st.spinner():
                toggle_like(post_id, user_name)
            st.rerun()

    with col_comment:
        st.markdown(
            f"<span style='font-size:0.9rem;color:#666;'>💬 {len(post_comments)} コメント</span>",
            unsafe_allow_html=True,
        )

    st.markdown("</div>", unsafe_allow_html=True)

    # ---- コメント一覧 ----
    with st.expander("コメントを見る / 書く"):
        if post_comments:
            for c in post_comments:
                st.markdown(
                    f"""
                    <div class="comment-item">
                        <span class="comment-author">{c['author']}</span>
                        <span class="comment-text">{c['comment']}</span>
                        <span class="comment-time">{c['timestamp']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("まだコメントがありません")

        if user_name:
            st.markdown("")
            new_comment = st.text_input(
                "コメント",
                key=f"ci_{post_id}",
                placeholder="コメントを入力...",
                label_visibility="collapsed",
            )
            if st.button("送信", key=f"cs_{post_id}", use_container_width=True):
                if new_comment.strip():
                    with st.spinner("送信中..."):
                        add_comment(post_id, user_name, new_comment.strip())
                    st.rerun()
                else:
                    st.warning("コメントを入力してください")
        else:
            st.caption("コメントするには名前を設定してください")

    st.markdown("</div>", unsafe_allow_html=True)
