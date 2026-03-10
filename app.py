import streamlit as st
from utils.styles import apply_styles, user_name_selector

st.set_page_config(
    page_title="寮アルバム",
    page_icon="📷",
    layout="centered",
)

apply_styles()
user_name = user_name_selector()

st.markdown(
    """
    <div class="home-hero">
        <h1>📷 寮アルバム</h1>
        <p>みんなの思い出を共有しよう</p>
    </div>
    """,
    unsafe_allow_html=True,
)

if user_name:
    st.markdown(
        f'<div style="text-align:center"><div class="user-badge">👋 こんにちは、{user_name}さん！</div></div>',
        unsafe_allow_html=True,
    )
else:
    st.info("👈 サイドバーで名前を入力するといいねやコメントができます")

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📷 アルバム")
    st.caption("写真一覧・いいね・コメント")
with col2:
    st.markdown("### 📸 写真投稿")
    st.caption("新しい写真をアップロード")

col3, col4 = st.columns(2)
with col3:
    st.markdown("### 📢 お知らせ")
    st.caption("寮からのお知らせ")
with col4:
    st.markdown("### 📋 寮の規約")
    st.caption("寮のルールを確認")
