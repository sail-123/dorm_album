"""
寮規約 - UI_SCREEN_SPEC.md #9 / SPEC.md #9 準拠
admin: 編集 / member: 閲覧
"""
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import get_rules, save_rule

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()

st.title(f"📋 {t('rules')}")

# ---- データ取得 ----
try:
    rules_list = get_rules()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

current_title = ""
current_content = ""
current_updated = ""
if rules_list:
    current_title = rules_list[0].get("title", "")
    current_content = rules_list[0].get("content", "")
    current_updated = rules_list[0].get("updated_at", "")


def show_rules(title: str, content: str, updated_at: str):
    if not content:
        st.info(t("no_data"))
        return
    if title:
        st.subheader(title)
    if updated_at:
        st.caption(f"🕐 {t('updated_at')}: {updated_at}")
    st.markdown("---")
    st.markdown(content.replace("\n", "  \n"))


# ---- 管理者: 編集モード ----
if _is_admin:
    editing = st.toggle(f"✏️ {t('edit_rules')}", value=False)

    if editing:
        with st.form("edit_rules_form"):
            r_title = st.text_input(
                t("title"), value=current_title, placeholder="寮規約"
            )
            r_content = st.text_area(
                t("content"),
                value=current_content,
                height=400,
                placeholder=t("rules_placeholder"),
            )
            if st.form_submit_button(f"💾 {t('save_rules')}", use_container_width=True):
                if r_title and r_content:
                    try:
                        save_rule(title=r_title, content=r_content)
                        st.success(t("rules_saved"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")
                else:
                    st.warning(t("fill_all_fields"))
    else:
        show_rules(current_title, current_content, current_updated)
else:
    # member: 閲覧のみ
    show_rules(current_title, current_content, current_updated)
