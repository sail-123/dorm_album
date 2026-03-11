"""
物品管理 - UI_SCREEN_SPEC.md #5 / SPEC.md #5 準拠
admin: 追加・編集・削除 / member: 閲覧のみ
"""
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import get_items, add_item, update_item, delete_item

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()

st.title(f"📦 {t('items')}")

STATUS_OPTIONS = ["in_stock", "out_of_stock", "need_purchase"]

# ---- データ取得 ----
try:
    items = get_items()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

# ---- 管理者: 物品追加 ----
if _is_admin:
    with st.expander(f"➕ {t('add_item')}"):
        with st.form("add_item_form"):
            c1, c2 = st.columns(2)
            with c1:
                i_name = st.text_input(t("item_name"), placeholder="ラップ")
                i_qty = st.text_input(t("quantity"), placeholder="2")
            with c2:
                i_loc = st.text_input(t("location"), placeholder="キッチン棚")
                i_status = st.selectbox(
                    t("status"), STATUS_OPTIONS,
                    format_func=lambda x: t(x),
                )
            if st.form_submit_button(t("add"), use_container_width=True):
                if i_name:
                    try:
                        add_item(
                            name=i_name, quantity=i_qty,
                            location=i_loc, status=i_status,
                        )
                        st.success(t("item_added"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")
                else:
                    st.warning(t("fill_all_fields"))

# ---- フィルター ----
col_f1, col_f2 = st.columns(2)
with col_f1:
    filter_status = st.selectbox(
        t("filter_status"),
        ["all_status"] + STATUS_OPTIONS,
        format_func=lambda x: t(x),
    )
with col_f2:
    search_name = st.text_input("🔍", placeholder=t("item_name"), label_visibility="collapsed")

# ---- 物品一覧（リスト表示） ----
filtered = items
if filter_status != "all_status":
    filtered = [i for i in filtered if i.get("status") == filter_status]
if search_name:
    filtered = [i for i in filtered if search_name.lower() in str(i.get("name", "")).lower()]

st.markdown(f"**{len(filtered)} {t('no_data') if not filtered else '件'}**")

if not filtered:
    st.info(t("no_data"))
else:
    for item in filtered:
        item_id = str(item.get("id", ""))
        name = item.get("name", "")
        qty = item.get("quantity", "")
        loc = item.get("location", "")
        status = item.get("status", "in_stock")

        status_badge_map = {
            "in_stock": f'<span class="badge-done">✅ {t("in_stock")}</span>',
            "out_of_stock": f'<span class="badge-unpaid">❌ {t("out_of_stock")}</span>',
            "need_purchase": f'<span class="badge-pending">🛒 {t("need_purchase")}</span>',
        }
        badge = status_badge_map.get(status, status)

        with st.container(border=True):
            col_info, col_btn = st.columns([4, 1])
            with col_info:
                st.markdown(f"**📦 {name}** &nbsp; {badge}", unsafe_allow_html=True)
                st.caption(f"数量: {qty}　　場所: {loc}")
            with col_btn:
                if _is_admin:
                    if st.button("✏️", key=f"edit_item_btn_{item_id}", help=t("edit")):
                        st.session_state[f"editing_item_{item_id}"] = True

        # 管理者: 編集フォーム
        if _is_admin and st.session_state.get(f"editing_item_{item_id}"):
            with st.form(f"edit_item_form_{item_id}"):
                st.subheader(t("edit_item"))
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_name = st.text_input(t("item_name"), value=name)
                    e_qty = st.text_input(t("quantity"), value=str(qty))
                with ec2:
                    e_loc = st.text_input(t("location"), value=loc)
                    e_status = st.selectbox(
                        t("status"), STATUS_OPTIONS,
                        format_func=lambda x: t(x),
                        index=STATUS_OPTIONS.index(status) if status in STATUS_OPTIONS else 0,
                    )

                s1, s2, s3 = st.columns(3)
                with s1:
                    if st.form_submit_button(t("save"), use_container_width=True):
                        try:
                            update_item(item_id, {
                                "name": e_name, "quantity": e_qty,
                                "location": e_loc, "status": e_status,
                            })
                            st.success(t("item_updated"))
                            del st.session_state[f"editing_item_{item_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
                with s2:
                    if st.form_submit_button(t("cancel"), use_container_width=True):
                        del st.session_state[f"editing_item_{item_id}"]
                        st.rerun()
                with s3:
                    if st.form_submit_button(f"🗑 {t('delete')}", use_container_width=True):
                        try:
                            delete_item(item_id)
                            st.success(t("item_deleted"))
                            del st.session_state[f"editing_item_{item_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
