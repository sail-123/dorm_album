import streamlit as st

MOBILE_CSS = """
<style>
/* ===== Mobile-first base ===== */
.stApp {
    background-color: #f0f2f5;
    color: #1a1a2e;
}

.main .block-container {
    max-width: 500px !important;
    padding: 0.5rem 0.75rem 4rem;
    margin: 0 auto;
}

/* ===== Post card ===== */
.post-card {
    background: #ffffff;
    border-radius: 16px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.1);
    margin-bottom: 1.25rem;
    overflow: hidden;
}

.post-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 1rem 0.5rem;
}

.post-author {
    font-weight: 700;
    font-size: 0.95rem;
    color: #1a1a2e;
}

.post-time {
    font-size: 0.72rem;
    color: #999;
}

.post-title {
    font-size: 1rem;
    font-weight: 700;
    padding: 0.4rem 1rem 0.2rem;
    color: #1a1a2e;
}

.post-caption {
    font-size: 0.88rem;
    padding: 0 1rem 0.75rem;
    color: #555;
    line-height: 1.55;
}

.post-actions {
    padding: 0.25rem 0.75rem 0.75rem;
    border-top: 1px solid #f5f5f5;
}

/* ===== Comments ===== */
.comment-item {
    padding: 0.5rem 0;
    border-bottom: 1px solid #f5f5f5;
}

.comment-item:last-child {
    border-bottom: none;
}

.comment-author {
    font-weight: 700;
    font-size: 0.84rem;
    color: #333;
    margin-right: 0.35rem;
}

.comment-text {
    font-size: 0.88rem;
    color: #444;
}

.comment-time {
    display: block;
    font-size: 0.70rem;
    color: #bbb;
    margin-top: 0.15rem;
}

/* ===== User badge ===== */
.user-badge {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 0.3rem 0.9rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    margin-bottom: 1rem;
}

/* ===== Home hero ===== */
.home-hero {
    text-align: center;
    padding: 1.5rem 0 1rem;
}

.home-hero h1 {
    font-size: 2rem;
    margin-bottom: 0.25rem;
    color: #1a1a2e;
}

.home-hero p {
    color: #444;
    font-size: 0.95rem;
}

/* ===== Buttons ===== */
div[data-testid="stButton"] > button {
    border-radius: 10px;
    font-size: 0.95rem;
    padding: 0.45rem 1rem;
}

/* ===== Sidebar ===== */
section[data-testid="stSidebar"] {
    background: #1a1a2e;
}

section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

section[data-testid="stSidebar"] input {
    color: #1a1a2e !important;
    background: #f0f2f5 !important;
    border-radius: 8px !important;
}
</style>
"""


def apply_styles():
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)


def user_name_selector() -> str:
    """サイドバーに名前入力を表示し、現在の名前を返す。"""
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""

    with st.sidebar:
        st.markdown("## 寮アルバム 📷")
        st.markdown("---")
        st.markdown("### 👤 あなたの名前")
        name = st.text_input(
            "名前",
            value=st.session_state.user_name,
            placeholder="例: 田中太郎",
            label_visibility="collapsed",
        )
        if name != st.session_state.user_name:
            st.session_state.user_name = name

        if st.session_state.user_name:
            st.success(f"ログイン中: {st.session_state.user_name}")

    return st.session_state.user_name
