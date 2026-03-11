"""
モバイルファーストのCSSスタイル
"""
import streamlit as st

MOBILE_CSS = """
<style>
/* ===== Mobile-first base ===== */
.stApp {
    background-color: #f0f2f5;
    color: #1a1a2e;
}

.main .block-container {
    max-width: 520px !important;
    padding: 0.5rem 0.75rem 4rem;
    margin: 0 auto;
    color: #1a1a2e;
}

/* Streamlit default text elements */
.stApp p, .stApp span, .stApp label,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp li, .stApp td, .stApp th,
.stMarkdown, .stMarkdown p,
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: #1a1a2e !important;
}

/* Metric values */
[data-testid="stMetricValue"],
[data-testid="stMetricLabel"],
[data-testid="stMetricDelta"] {
    color: #1a1a2e !important;
}

/* Input labels */
.stTextInput label, .stSelectbox label,
.stTextArea label, .stNumberInput label,
.stDateInput label, .stCheckbox label,
.stRadio label {
    color: #1a1a2e !important;
}

/* ===== Card ===== */
.dorm-card {
    background: #ffffff;
    border-radius: 14px;
    box-shadow: 0 1px 6px rgba(0,0,0,0.08);
    padding: 1rem;
    margin-bottom: 1rem;
}

/* ===== Post card (album) ===== */
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
}

.post-time {
    font-size: 0.72rem;
    color: #999;
}

.post-title {
    font-size: 1rem;
    font-weight: 700;
    padding: 0.4rem 1rem 0.2rem;
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

/* ===== Status badge ===== */
.badge-pending {
    display: inline-block;
    background: #fff3cd;
    color: #856404;
    padding: 0.15rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-done {
    display: inline-block;
    background: #d1e7dd;
    color: #0a3622;
    padding: 0.15rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-paid {
    display: inline-block;
    background: #d1e7dd;
    color: #0a3622;
    padding: 0.15rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
}

.badge-unpaid {
    display: inline-block;
    background: #f8d7da;
    color: #842029;
    padding: 0.15rem 0.6rem;
    border-radius: 12px;
    font-size: 0.8rem;
    font-weight: 600;
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
    margin-bottom: 0.5rem;
}

/* ===== Login hero ===== */
.login-hero {
    text-align: center;
    padding: 2rem 0 1.5rem;
}

.login-hero h1 {
    font-size: 2.2rem;
    margin-bottom: 0.3rem;
}

.login-hero p {
    color: #555;
    font-size: 0.95rem;
}

/* ===== Buttons ===== */
div[data-testid="stButton"] > button {
    border-radius: 10px;
    font-size: 0.95rem;
    padding: 0.45rem 1rem;
    background-color: #667eea;
    color: #ffffff !important;
    border: none;
}

div[data-testid="stButton"] > button:hover,
div[data-testid="stButton"] > button:focus {
    background-color: #764ba2;
    color: #ffffff !important;
    border: none;
}

div[data-testid="stButton"] > button[kind="secondary"] {
    background-color: #e8eaf6;
    color: #1a1a2e !important;
    border: 1px solid #c5cae9;
}

div[data-testid="stButton"] > button[kind="secondary"]:hover {
    background-color: #c5cae9;
    color: #1a1a2e !important;
}

/* Form submit buttons */
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 10px;
    font-size: 0.95rem;
    padding: 0.45rem 1rem;
    background-color: #667eea;
    color: #ffffff !important;
    border: none;
}

div[data-testid="stFormSubmitButton"] > button:hover,
div[data-testid="stFormSubmitButton"] > button:focus {
    background-color: #764ba2;
    color: #ffffff !important;
    border: none;
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

section[data-testid="stSidebar"] .stSelectbox > div {
    color: #1a1a2e !important;
    background: #f0f2f5 !important;
}

/* ===== Grid for albums ===== */
.album-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 1rem;
}

.album-grid img {
    border-radius: 8px;
    width: 100%;
    object-fit: cover;
    aspect-ratio: 1;
}

/* ===== Announcement card ===== */
.announce-card {
    background: #fff;
    border-left: 4px solid #667eea;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
</style>
"""


def apply_styles():
    st.markdown(MOBILE_CSS, unsafe_allow_html=True)
