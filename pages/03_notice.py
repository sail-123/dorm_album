import streamlit as st

st.title("📷 写真投稿")

title = st.text_input("タイトル")

comment = st.text_area("コメント")

image = st.file_uploader(
    "写真をアップロード",
    type=["png","jpg","jpeg"]
)

if st.button("投稿"):
    st.success("投稿処理は未実装です")
