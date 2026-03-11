"""
寮管理アプリ - メインエントリーポイント
ログイン画面 + ナビゲーション管理
"""
import streamlit as st
from utils.auth import is_logged_in, get_user, login_user, logout, hash_password
from utils.i18n import t, get_lang, set_lang, LANGUAGES
from utils.styles import apply_styles

st.set_page_config(
    page_title="メゾン美崎",
    page_icon="🏠",
    layout="centered",
    initial_sidebar_state="expanded",
)

apply_styles()

# ---- 言語選択（常にサイドバーに表示） ----
with st.sidebar:
    lang_keys = list(LANGUAGES.keys())
    lang_labels = list(LANGUAGES.values())
    current_lang = get_lang()
    current_idx = lang_keys.index(current_lang) if current_lang in lang_keys else 0

    selected_idx = st.selectbox(
        "🌐 " + t("language"),
        options=range(len(lang_keys)),
        format_func=lambda i: lang_labels[i],
        index=current_idx,
        key="lang_selectbox",
    )
    new_lang = lang_keys[selected_idx]
    if new_lang != current_lang:
        set_lang(new_lang)
        st.rerun()

# ---- 未ログイン: ログイン画面 ----
if not is_logged_in():
    st.markdown(
        f"""
        <div class="login-hero">
            <h1>🏠</h1>
            <h2>{t('app_title')}</h2>
            <p>メゾン美崎メンバー専用グループウェア</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 初期管理者作成フォーム（メンバーが0人の場合）
    try:
        from utils.gsheets import get_members_with_password
        members = get_members_with_password()
        is_empty = len(members) == 0
    except Exception:
        is_empty = False

    if is_empty:
        st.info(t("setup_description"))
        with st.form("setup_form"):
            st.subheader(t("setup_first_admin"))
            s_name = st.text_input(t("name"), placeholder="田中 太郎")
            s_email = st.text_input(t("email"), placeholder="admin@example.com")
            s_pw = st.text_input(t("password"), type="password")
            s_pw2 = st.text_input(t("confirm_password"), type="password")
            if st.form_submit_button(t("create_admin"), use_container_width=True):
                if s_name and s_email and s_pw:
                    if s_pw != s_pw2:
                        st.error(t("password_mismatch"))
                    else:
                        from utils.gsheets import add_member
                        from datetime import date
                        new_id = add_member(
                            name=s_name, room="", phone="", email=s_email,
                            role="admin", join_date=str(date.today()),
                            password_hash=hash_password(s_pw),
                        )
                        st.session_state._new_admin_id = new_id
                        st.rerun()
                else:
                    st.warning(t("fill_all_fields"))
    else:
        if "_new_admin_id" in st.session_state:
            st.success(t("admin_created"))
            st.info(f"🔑 {t('user_id')}: **`{st.session_state._new_admin_id}`**")

        with st.form("login_form"):
            user_id_input = st.text_input(t("user_id"), placeholder="a1b2c3d4")
            password = st.text_input(t("password"), type="password")
            submitted = st.form_submit_button(t("login_btn"), use_container_width=True)

        if submitted:
            if user_id_input and password:
                with st.spinner(t("loading")):
                    success = login_user(user_id_input, password)
                if success:
                    if "_new_admin_id" in st.session_state:
                        del st.session_state._new_admin_id
                    st.rerun()
                else:
                    st.error(t("login_error"))
            else:
                st.warning(t("fill_all_fields"))

# ---- ログイン済み: ナビゲーション ----
else:
    user = get_user()

    # サイドバー: ユーザー情報とログアウト
    with st.sidebar:
        st.markdown("---")
        st.markdown(
            f'<div class="user-badge">👤 {user["name"]}</div>',
            unsafe_allow_html=True,
        )
        role_label = "🔑 Admin" if user.get("role") == "admin" else "👥 Member"
        st.caption(role_label)
        if st.button(f"🚪 {t('logout')}", use_container_width=True):
            logout()
            st.rerun()
        st.markdown("---")

    # ページ定義（SYSTEM_ARCHITECTURE.md 準拠）
    pages = [
        st.Page("pages/dashboard.py",     title=t("dashboard"),     icon="🏠"),
        st.Page("pages/members.py",        title=t("members"),        icon="👥"),
        st.Page("pages/cleaning.py",       title=t("cleaning"),       icon="🧹"),
        st.Page("pages/payments.py",       title=t("payments"),       icon="💰"),
        st.Page("pages/items.py",          title=t("items"),          icon="📦"),
        st.Page("pages/albums.py",         title=t("albums"),         icon="📷"),
        st.Page("pages/announcements.py",  title=t("announcements"),  icon="📢"),
        st.Page("pages/boards.py",         title=t("boards"),         icon="💬"),
        st.Page("pages/rules.py",          title=t("rules"),          icon="📋"),
    ]

    if user.get("role") == "admin":
        pages.append(st.Page("pages/admin.py", title=t("admin"), icon="⚙️"))

    pg = st.navigation(pages)
    pg.run()
