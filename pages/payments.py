"""
集金管理 - UI_SCREEN_SPEC.md #4 / SPEC.md #4 準拠
admin: 集金作成・支払い管理 / member: 支払い状況確認
"""
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_payments, get_payment_status, get_members,
    add_payment, update_payment, delete_payment, set_payment_status,
)
from datetime import date, timedelta

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()

st.title(f"💰 {t('payments')}")

# ---- データ取得 ----
try:
    payments = get_payments()
    statuses = get_payment_status()
    members_list = get_members()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

members_map = {str(m["id"]): m["name"] for m in members_list}

# paid_ids for current user
user_paid_ids = {
    str(s["payment_id"])
    for s in statuses
    if str(s.get("member_id", "")) == str(user["id"])
    and str(s.get("paid", "")).lower() == "true"
}

# ---- 管理者: 集金作成 ----
if _is_admin:
    with st.expander(f"➕ {t('add_payment')}"):
        with st.form("add_payment_form"):
            c1, c2 = st.columns(2)
            with c1:
                p_title = st.text_input(t("payment_name"), placeholder="寮費 4月分")
                p_amount = st.number_input(t("amount"), min_value=0, step=100, value=5000)
            with c2:
                p_due = st.date_input(t("due_date"), value=date.today() + timedelta(days=14))
                p_desc = st.text_input(t("description"), placeholder="任意")
            if st.form_submit_button(t("add"), use_container_width=True):
                if p_title:
                    try:
                        add_payment(
                            title=p_title,
                            amount=str(p_amount),
                            due_date=str(p_due),
                            description=p_desc,
                        )
                        st.success(t("payment_added"))
                        st.rerun()
                    except Exception as e:
                        st.error(f"{t('error')}: {e}")
                else:
                    st.warning(t("fill_all_fields"))

# ---- 集金一覧（カード表示） ----
if not payments:
    st.info(t("no_data"))
else:
    for payment in payments:
        pay_id = str(payment.get("id", ""))
        title = payment.get("title", "")
        amount = payment.get("amount", "")
        due_date = payment.get("due_date", "")
        description = payment.get("description", "")

        # 自分の支払い状況
        is_paid = pay_id in user_paid_ids

        with st.container(border=True):
            col_info, col_action = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{title}**")
                st.write(f"💴 ¥{amount}　　📅 {t('due_date')}: {due_date}")
                if description:
                    st.caption(description)
                if is_paid:
                    st.markdown(
                        f'<span class="badge-paid">✅ {t("paid")}</span>',
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f'<span class="badge-unpaid">⚠️ {t("unpaid")}</span>',
                        unsafe_allow_html=True,
                    )
            with col_action:
                if _is_admin:
                    if st.button("✏️", key=f"edit_pay_{pay_id}", help=t("edit")):
                        st.session_state[f"editing_pay_{pay_id}"] = True

        # 管理者: メンバー別支払い状況
        if _is_admin:
            with st.expander(f"👥 {t('member_payment_status')}"):
                # payment_idに紐づくstatusを集計
                pay_statuses = {
                    str(s["member_id"]): str(s.get("paid", "false")).lower()
                    for s in statuses
                    if str(s.get("payment_id", "")) == pay_id
                }
                paid_count = sum(1 for v in pay_statuses.values() if v == "true")
                total = len(members_list)
                st.caption(f"✅ {paid_count}/{total} {t('paid')}")

                for member in members_list:
                    mid = str(member["id"])
                    mname = member["name"]
                    m_paid = pay_statuses.get(mid, "false") == "true"
                    mc1, mc2 = st.columns([3, 1])
                    with mc1:
                        badge = (
                            f'<span class="badge-paid">✅ {t("paid")}</span>'
                            if m_paid
                            else f'<span class="badge-unpaid">⚠️ {t("unpaid")}</span>'
                        )
                        st.markdown(f"{mname} &nbsp; {badge}", unsafe_allow_html=True)
                    with mc2:
                        if m_paid:
                            if st.button(t("mark_unpaid"), key=f"unpay_{pay_id}_{mid}"):
                                set_payment_status(pay_id, mid, False)
                                st.success(t("payment_status_updated"))
                                st.rerun()
                        else:
                            if st.button(t("mark_paid"), key=f"paid_{pay_id}_{mid}"):
                                set_payment_status(pay_id, mid, True)
                                st.success(t("payment_status_updated"))
                                st.rerun()

        # 管理者: 編集フォーム
        if _is_admin and st.session_state.get(f"editing_pay_{pay_id}"):
            with st.form(f"edit_pay_form_{pay_id}"):
                st.subheader(t("edit_payment"))
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_title = st.text_input(t("payment_name"), value=title)
                    e_amount = st.text_input(t("amount"), value=str(amount))
                with ec2:
                    e_due = st.text_input(t("due_date"), value=due_date)
                    e_desc = st.text_input(t("description"), value=description)

                s1, s2, s3 = st.columns(3)
                with s1:
                    if st.form_submit_button(t("save"), use_container_width=True):
                        try:
                            update_payment(pay_id, {
                                "title": e_title, "amount": e_amount,
                                "due_date": e_due, "description": e_desc,
                            })
                            st.success(t("payment_updated"))
                            del st.session_state[f"editing_pay_{pay_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
                with s2:
                    if st.form_submit_button(t("cancel"), use_container_width=True):
                        del st.session_state[f"editing_pay_{pay_id}"]
                        st.rerun()
                with s3:
                    if st.form_submit_button(f"🗑 {t('delete')}", use_container_width=True):
                        try:
                            delete_payment(pay_id)
                            st.success(t("payment_deleted"))
                            del st.session_state[f"editing_pay_{pay_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
