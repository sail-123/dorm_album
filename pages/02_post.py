import streamlit as st
from utils.sheets import save_post
from utils.cloudinary import upload_image
from utils.styles import apply_styles, user_name_selector

st.set_page_config(
    page_title="写真投稿 | 寮アルバム",
    page_icon="📸",
    layout="centered",
)

apply_styles()
user_name = user_name_selector()

st.title("📸 写真投稿")

if not user_name:
    st.warning("👈 サイドバーで名前を入力してから投稿してください")
    st.stop()

st.markdown(
    f'<div class="user-badge">投稿者: {user_name}</div>',
    unsafe_allow_html=True,
)

with st.form("post_form", clear_on_submit=True):
    title = st.text_input(
        "タイトル *",
        placeholder="写真のタイトルを入力",
        max_chars=50,
    )
    caption = st.text_area(
        "キャプション",
        placeholder="写真の説明やひとことコメント",
        height=100,
        max_chars=300,
    )
    image_file = st.file_uploader(
        "写真をアップロード *",
        type=["png", "jpg", "jpeg", "heic", "webp"],
        help="スマホで撮影した写真をそのままアップロードできます",
    )

    submitted = st.form_submit_button(
        "📤 投稿する",
        use_container_width=True,
        type="primary",
    )

if submitted:
    if not title:
        st.error("タイトルを入力してください")
    elif not image_file:
        st.error("写真を選択してください")
    else:
        try:
            with st.spinner("アップロード中..."):
                image_url = upload_image(image_file)
            with st.spinner("保存中..."):
                save_post(user_name, title, caption or "", image_url)
            st.success("投稿しました！🎉")
            st.balloons()
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
