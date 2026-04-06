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
    delete_cleaning_task,
)
from datetime import date

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()

st.title(f"🧹 {t('cleaning')}")

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
            if member_id and st.session_state.add_task_dates:
                try:
                    add_cleaning_task(
                        member_id=member_id,
                        location="",
                        dates=json.dumps(st.session_state.add_task_dates),
                    )
                    st.session_state.add_task_dates = []
                    st.success(t("task_added"))
                    st.rerun()
                except Exception as e:
                    st.error(f"{t('error')}: {e}")
            else:
                st.warning(t("fill_all_fields"))

# ---- 当月の掃除当番（日付順表示） ----
today = date.today()
current_year = today.year
current_month = today.month

tasks_by_id = {str(task.get("id", "")): task for task in tasks}

# 全タスクの日付を展開し、当月分のみ抽出
date_entries = []
for task in tasks:
    task_dates = _parse_dates(task.get("dates", []))
    for d_str in task_dates:
        try:
            d = date.fromisoformat(d_str)
            if d.year == current_year and d.month == current_month:
                date_entries.append({
                    "date": d,
                    "date_str": d_str,
                    "task_id": str(task.get("id", "")),
                    "member_id": str(task.get("member_id", "")),
                    "member_name": members_map.get(str(task.get("member_id", "")), "?"),
                    "location": task.get("location", ""),
                })
        except Exception:
            pass

# 日付順にソート
date_entries.sort(key=lambda x: x["date"])

st.subheader(f"📅 {current_year}年{current_month}月")

if not date_entries:
    st.info(t("no_data"))
else:
    # 日付でグループ化
    from collections import defaultdict
    entries_by_date = defaultdict(list)
    for entry in date_entries:
        entries_by_date[entry["date_str"]].append(entry)

    sorted_dates = sorted(entries_by_date.keys())

    for d_str in sorted_dates:
        day_entries = entries_by_date[d_str]
        num_members = len(day_entries)

        with st.container(border=True):
            # 日付 + メンバーを横並びで1行表示
            cols = st.columns([2] + [3] * num_members)
            with cols[0]:
                st.markdown(f"**📅 {d_str}**")
            for i, entry in enumerate(day_entries):
                with cols[i + 1]:
                    st.markdown(
                        f"👤 **{entry['member_name']}**",
                        unsafe_allow_html=True,
                    )

        # 管理者: 編集・削除（エントリごと）
        if _is_admin:
            for entry in day_entries:
                task_id = entry["task_id"]
                member_name = entry["member_name"]
                row_key = f"{task_id}_{d_str}"
                edit_key = f"edit_task_{row_key}"
                edit_dates_key = f"edit_task_dates_{row_key}"
                task = tasks_by_id.get(task_id, {})
                task_all_dates = _parse_dates(task.get("dates", []))

                if st.session_state.get(edit_key):
                    if edit_dates_key not in st.session_state:
                        st.session_state[edit_dates_key] = list(task_all_dates)

                    st.markdown(f"**✏️ {t('edit_task')}** — 👤 {member_name}")
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_member = st.selectbox(
                            t("select_member"),
                            options=members_names,
                            index=members_names.index(member_name) if member_name in members_names else 0,
                            key=f"edit_member_{row_key}",
                        )
                    with ec2:
                        st.date_input(
                            t("add_date"), value=date.today(),
                            key=f"edit_date_pick_{row_key}",
                        )
                        if st.button(f"📅 {t('add_date')}", key=f"edit_date_add_{row_key}"):
                            new_date_str = str(st.session_state[f"edit_date_pick_{row_key}"])
                            if new_date_str not in st.session_state[edit_dates_key]:
                                st.session_state[edit_dates_key].append(new_date_str)
                                st.session_state[edit_dates_key].sort()
                            st.rerun()

                    if st.session_state[edit_dates_key]:
                        st.write(f"**{t('selected_dates')}:**")
                        for i, dd in enumerate(list(st.session_state[edit_dates_key])):
                            dc1, dc2 = st.columns([5, 1])
                            dc1.write(f"📅 {dd}")
                            if dc2.button("✕", key=f"rm_edit_date_{row_key}_{i}"):
                                st.session_state[edit_dates_key].pop(i)
                                st.rerun()
                    else:
                        st.caption(f"⚠️ {t('no_dates_selected')}")

                    s1, s2, s3 = st.columns(3)
                    with s1:
                        if st.button(t("save"), key=f"save_{row_key}", use_container_width=True):
                            try:
                                update_cleaning_task(task_id, {
                                    "member_id": members_options.get(e_member, ""),
                                    "dates": json.dumps(st.session_state[edit_dates_key]),
                                })
                                st.success(t("task_updated"))
                                del st.session_state[edit_key]
                                st.session_state.pop(edit_dates_key, None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"{t('error')}: {e}")
                    with s2:
                        if st.button(t("cancel"), key=f"cancel_{row_key}", use_container_width=True):
                            del st.session_state[edit_key]
                            st.session_state.pop(edit_dates_key, None)
                            st.rerun()
                    with s3:
                        if st.button(f"🗑 {t('delete')}", key=f"delete_{row_key}", use_container_width=True):
                            try:
                                delete_cleaning_task(task_id)
                                st.success(t("task_deleted"))
                                del st.session_state[edit_key]
                                st.session_state.pop(edit_dates_key, None)
                                st.rerun()
                            except Exception as e:
                                st.error(f"{t('error')}: {e}")
                else:
                    if st.button(f"✏️ {t('edit')} ({member_name})", key=f"edit_task_btn_{row_key}"):
                        st.session_state[edit_key] = True
                        st.rerun()
