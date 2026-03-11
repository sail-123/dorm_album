"""
掃除当番管理 - UI_SCREEN_SPEC.md #3 / SPEC.md #3 準拠
admin: 登録・編集・削除 / member: 確認・完了チェック
"""
import json
import streamlit as st
from utils.auth import require_auth, get_user, is_admin
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import (
    get_cleaning_tasks, get_members,
    add_cleaning_task, update_cleaning_task,
    complete_cleaning_task, delete_cleaning_task,
)
from datetime import date

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()

st.title(f"🧹 {t('cleaning')}")

LOCATIONS = [t("kitchen"), t("garbage")]

# ---- データ取得 ----
try:
    tasks = get_cleaning_tasks()
    members_list = get_members()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

members_map = {str(m["id"]): m["name"] for m in members_list}
members_options = {m["name"]: str(m["id"]) for m in members_list}
members_names = list(members_options.keys())


def _parse_dates(raw) -> list:
    if isinstance(raw, list):
        return raw
    try:
        return json.loads(raw) if raw else []
    except Exception:
        return [d.strip() for d in str(raw).split(",") if d.strip()]


# ---- 管理者: 当番追加 ----
if _is_admin:
    if "add_task_dates" not in st.session_state:
        st.session_state.add_task_dates = []

    with st.expander(f"➕ {t('add_task')}"):
        c1, c2 = st.columns(2)
        with c1:
            st.selectbox(
                t("select_member"),
                options=members_names,
                key="add_task_member",
            )
            st.selectbox(t("select_location"), LOCATIONS, key="add_task_location")
        with c2:
            st.date_input(t("add_date"), value=date.today(), key="add_task_date_pick")
            if st.button(f"📅 {t('add_date')}", key="add_task_date_btn"):
                date_str = str(st.session_state.add_task_date_pick)
                if date_str not in st.session_state.add_task_dates:
                    st.session_state.add_task_dates.append(date_str)
                    st.session_state.add_task_dates.sort()
                st.rerun()

        if st.session_state.add_task_dates:
            st.write(f"**{t('selected_dates')}:**")
            for i, d in enumerate(list(st.session_state.add_task_dates)):
                dc1, dc2 = st.columns([5, 1])
                dc1.write(f"📅 {d}")
                if dc2.button("✕", key=f"rm_new_date_{i}"):
                    st.session_state.add_task_dates.pop(i)
                    st.rerun()
        else:
            st.caption(f"⚠️ {t('no_dates_selected')}")

        if st.button(t("add"), key="add_task_submit", use_container_width=True):
            member_id = members_options.get(st.session_state.get("add_task_member", ""), "")
            location = st.session_state.get("add_task_location", LOCATIONS[0])
            if member_id and st.session_state.add_task_dates:
                try:
                    add_cleaning_task(
                        member_id=member_id,
                        location=location,
                        dates=json.dumps(st.session_state.add_task_dates),
                    )
                    st.session_state.add_task_dates = []
                    st.success(t("task_added"))
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('error')}: {e}")
            else:
                st.warning(t("fill_all_fields"))

# ---- フィルター ----
st.markdown("---")
col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    show_filter = st.selectbox(
        t("filter_status"),
        ["all_status", "pending", "done"],
        format_func=lambda x: t(x),
    )
with col_filter2:
    my_tasks_only = st.checkbox(t("my_tasks"))

# ---- 当番一覧（リスト表示） ----
filtered = tasks
if show_filter != "all_status":
    filtered = [t2 for t2 in filtered if t2.get("status") == show_filter]
if my_tasks_only:
    filtered = [t2 for t2 in filtered if str(t2.get("member_id", "")) == str(user["id"])]

if not filtered:
    st.info(t("no_data"))
else:
    for task in filtered:
        task_id = str(task.get("id", ""))
        member_name = members_map.get(str(task.get("member_id", "")), "?")
        location = task.get("location", "")
        dates = _parse_dates(task.get("dates", []))
        dates_str = ", ".join(dates) if dates else "-"
        status = task.get("status", "pending")

        with st.container(border=True):
            col_left, col_right = st.columns([3, 1])
            with col_left:
                status_badge = (
                    f'<span class="badge-done">✅ {t("done")}</span>'
                    if status == "done"
                    else f'<span class="badge-pending">⏳ {t("pending")}</span>'
                )
                st.markdown(
                    f"**📍 {location}** &nbsp; {status_badge}",
                    unsafe_allow_html=True,
                )
                st.caption(f"👤 {member_name}　　📅 {dates_str}")
            with col_right:
                if status == "pending":
                    if _is_admin or str(task.get("member_id", "")) == str(user["id"]):
                        if st.button("✅", key=f"done_{task_id}", help=t("mark_done")):
                            try:
                                complete_cleaning_task(task_id)
                                st.success(t("task_completed"))
                                st.rerun()
                            except Exception as e:
                                st.error(f"{t('error')}: {e}")

        # 管理者: 編集・削除
        if _is_admin:
            edit_key = f"edit_task_{task_id}"
            edit_dates_key = f"edit_task_dates_{task_id}"

            if st.session_state.get(edit_key):
                if edit_dates_key not in st.session_state:
                    st.session_state[edit_dates_key] = list(dates)

                st.markdown(f"**✏️ {t('edit_task')}**")
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_member = st.selectbox(
                        t("select_member"),
                        options=members_names,
                        index=members_names.index(member_name) if member_name in members_names else 0,
                        key=f"edit_member_{task_id}",
                    )
                    e_loc = st.selectbox(
                        t("select_location"), LOCATIONS,
                        index=LOCATIONS.index(location) if location in LOCATIONS else 0,
                        key=f"edit_loc_{task_id}",
                    )
                with ec2:
                    st.date_input(
                        t("add_date"), value=date.today(),
                        key=f"edit_date_pick_{task_id}",
                    )
                    if st.button(f"📅 {t('add_date')}", key=f"edit_date_add_{task_id}"):
                        date_str = str(st.session_state[f"edit_date_pick_{task_id}"])
                        if date_str not in st.session_state[edit_dates_key]:
                            st.session_state[edit_dates_key].append(date_str)
                            st.session_state[edit_dates_key].sort()
                        st.rerun()

                if st.session_state[edit_dates_key]:
                    st.write(f"**{t('selected_dates')}:**")
                    for i, d in enumerate(list(st.session_state[edit_dates_key])):
                        dc1, dc2 = st.columns([5, 1])
                        dc1.write(f"📅 {d}")
                        if dc2.button("✕", key=f"rm_edit_date_{task_id}_{i}"):
                            st.session_state[edit_dates_key].pop(i)
                            st.rerun()
                else:
                    st.caption(f"⚠️ {t('no_dates_selected')}")

                s1, s2, s3 = st.columns(3)
                with s1:
                    if st.button(t("save"), key=f"save_{task_id}", use_container_width=True):
                        try:
                            update_cleaning_task(task_id, {
                                "member_id": members_options.get(e_member, ""),
                                "location": e_loc,
                                "dates": json.dumps(st.session_state[edit_dates_key]),
                            })
                            st.success(t("task_updated"))
                            del st.session_state[edit_key]
                            st.session_state.pop(edit_dates_key, None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
                with s2:
                    if st.button(t("cancel"), key=f"cancel_{task_id}", use_container_width=True):
                        del st.session_state[edit_key]
                        st.session_state.pop(edit_dates_key, None)
                        st.rerun()
                with s3:
                    if st.button(f"🗑 {t('delete')}", key=f"delete_{task_id}", use_container_width=True):
                        try:
                            delete_cleaning_task(task_id)
                            st.success(t("task_deleted"))
                            del st.session_state[edit_key]
                            st.session_state.pop(edit_dates_key, None)
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
            else:
                if st.button(f"✏️ {t('edit')}", key=f"edit_task_btn_{task_id}"):
                    st.session_state[edit_key] = True
                    st.rerun()
