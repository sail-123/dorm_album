"""
メンバー管理 - UI_SCREEN_SPEC.md #2 / PERMISSION_SPEC.md 準拠
admin: CRUD操作可能 / member: 自分の情報のみ編集可
"""
import streamlit as st
from utils.auth import require_auth, get_user, is_admin, hash_password
from utils.i18n import t
from utils.styles import apply_styles
from utils.gsheets import get_members, add_member, update_member, delete_member
from utils.cloudinary import upload_member_photo, delete_member_photo

apply_styles()
require_auth()
user = get_user()
_is_admin = is_admin()
current_user_id = str(user["id"])

st.title(f"👥 {t('members')}")

# ---- データ取得 ----
try:
    members = get_members()
except Exception as e:
    st.error(f"{t('error')}: {e}")
    st.stop()

# ---- 管理者: メンバー追加フォーム ----
if _is_admin:
    with st.expander(f"➕ {t('add_member')}"):
        with st.form("add_member_form"):
            c1, c2 = st.columns(2)
            with c1:
                n_name = st.text_input(t("name"), placeholder="田中 太郎")
                n_user_id = st.text_input(t("user_id"), placeholder="tanaka01",
                                          help=t("user_id_hint"))
                n_role = st.selectbox(t("role"), ["member", "admin"])
            with c2:
                n_pw = st.text_input(t("new_password"), type="password")
                n_pw2 = st.text_input(t("confirm_password"), type="password")
            st.markdown(f"##### {t('optional_fields')}")
            oc1, oc2 = st.columns(2)
            with oc1:
                n_room = st.text_input(t("room"), placeholder="101")
                n_phone = st.text_input(t("phone"), placeholder="090-0000-0000")
                n_gender = st.text_input(t("gender"), placeholder="男性 / 女性")
            with oc2:
                n_email = st.text_input(t("email"), placeholder="taro@example.com")
                n_join = st.text_input(t("join_date"), placeholder="2024-04-01")
                n_nationality = st.text_input(t("nationality"), placeholder="日本")
            if st.form_submit_button(t("add"), use_container_width=True):
                if n_name and n_pw:
                    if n_pw != n_pw2:
                        st.error(t("password_mismatch"))
                    else:
                        try:
                            new_id = add_member(
                                name=n_name, room=n_room, phone=n_phone,
                                email=n_email, role=n_role,
                                join_date=n_join,
                                password_hash=hash_password(n_pw),
                                user_id=n_user_id,
                                gender=n_gender,
                                nationality=n_nationality,
                            )
                            st.success(t("member_added"))
                            st.info(f"🔑 {t('user_id')}: **`{new_id}`**")
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
                else:
                    st.warning(t("fill_all_fields"))

# ---- メンバー一覧（テーブル表示） ----
st.markdown(f"### {t('member_list')} ({len(members)}人)")

if not members:
    st.info(t("no_data"))
else:
    for member in members:
        member_id = str(member.get("id", ""))
        name = member.get("name", "")
        room = member.get("room", "")
        phone = member.get("phone", "")
        email = member.get("email", "")
        role = member.get("role", "member")
        join_date = member.get("join_date", "")
        gender = member.get("gender", "")
        nationality = member.get("nationality", "")
        photo_url = member.get("photo_url", "")

        is_self = member_id == current_user_id
        can_edit = _is_admin or is_self

        with st.container(border=True):
            col_photo, col_info, col_btn = st.columns([1, 4, 1])
            with col_photo:
                if photo_url:
                    st.image(photo_url, width=60)
                else:
                    st.markdown("👤")
            with col_info:
                role_badge = "🔑" if role == "admin" else "👤"
                st.markdown(f"**{role_badge} {name}**  　部屋: {room}")
                extra = "  ".join(filter(None, [
                    f"🚻 {gender}" if gender else "",
                    f"🌏 {nationality}" if nationality else "",
                ]))
                st.caption(f"📞 {phone}　　✉️ {email}　　📅 {join_date}")
                if extra:
                    st.caption(extra)
            with col_btn:
                if can_edit:
                    if st.button("✏️", key=f"edit_btn_{member_id}", help=t("edit")):
                        st.session_state[f"editing_{member_id}"] = True
                else:
                    # member権限で他メンバーを閲覧する場合は詳細ボタンを表示
                    detail_open = st.session_state.get(f"detail_{member_id}", False)
                    label = "🔼" if detail_open else "👁"
                    if st.button(label, key=f"detail_btn_{member_id}", help=t("member_detail")):
                        st.session_state[f"detail_{member_id}"] = not detail_open
                        st.rerun()

        # 詳細表示（読み取り専用 - member権限で他のメンバーを閲覧）
        if not can_edit and st.session_state.get(f"detail_{member_id}"):
            with st.container(border=True):
                st.markdown(f"#### {t('member_detail')}")
                if photo_url:
                    st.image(photo_url, width=120)
                dc1, dc2 = st.columns(2)
                with dc1:
                    st.text_input(t("name"), value=name, disabled=True,
                                  key=f"dv_name_{member_id}")
                    st.text_input(t("room"), value=room, disabled=True,
                                  key=f"dv_room_{member_id}")
                    st.text_input(t("phone"), value=phone, disabled=True,
                                  key=f"dv_phone_{member_id}")
                    st.text_input(t("gender"), value=gender, disabled=True,
                                  key=f"dv_gender_{member_id}")
                with dc2:
                    st.text_input(t("email"), value=email, disabled=True,
                                  key=f"dv_email_{member_id}")
                    st.text_input(t("join_date"), value=join_date, disabled=True,
                                  key=f"dv_join_{member_id}")
                    st.text_input(t("nationality"), value=nationality, disabled=True,
                                  key=f"dv_nationality_{member_id}")
                    role_label = "🔑 admin" if role == "admin" else "👤 member"
                    st.text_input(t("role"), value=role_label, disabled=True,
                                  key=f"dv_role_{member_id}")
                if st.button(t("close"), key=f"close_detail_{member_id}",
                             use_container_width=True):
                    st.session_state[f"detail_{member_id}"] = False
                    st.rerun()

        # 編集フォーム
        if can_edit and st.session_state.get(f"editing_{member_id}"):
            with st.container(border=True):
                st.subheader(t("edit_member"))

                # --- 顔写真アップロード・削除（フォーム外で処理）---
                st.markdown(f"**{t('photo')}**")
                if photo_url:
                    ph_col1, ph_col2 = st.columns([3, 1])
                    with ph_col1:
                        st.image(photo_url, width=120)
                    with ph_col2:
                        if st.button(f"🗑 {t('delete_photo')}", key=f"delete_photo_{member_id}"):
                            with st.spinner(t("saving")):
                                try:
                                    delete_member_photo(photo_url)
                                    update_member(member_id, {"photo_url": ""})
                                    st.success(t("member_photo_deleted"))
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"{t('error')}: {e}")
                uploaded_photo = st.file_uploader(
                    t("upload_photo"),
                    type=["jpg", "jpeg", "png"],
                    key=f"photo_upload_{member_id}",
                )
                if uploaded_photo is not None:
                    if st.button(t("save_photo"), key=f"save_photo_{member_id}"):
                        with st.spinner(t("uploading")):
                            try:
                                new_photo_url = upload_member_photo(uploaded_photo)
                                update_member(member_id, {"photo_url": new_photo_url})
                                st.success(t("photo_saved"))
                                st.rerun()
                            except Exception as e:
                                st.error(f"{t('error')}: {e}")

                st.divider()

                with st.form(f"edit_form_{member_id}"):
                    ec1, ec2 = st.columns(2)
                    with ec1:
                        e_name = st.text_input(t("name"), value=name)
                        e_room = st.text_input(t("room"), value=room)
                        e_phone = st.text_input(t("phone"), value=phone)
                        e_gender = st.text_input(t("gender"), value=gender)
                    with ec2:
                        e_email = st.text_input(t("email"), value=email)
                        e_join = st.text_input(t("join_date"), value=join_date)
                        e_nationality = st.text_input(t("nationality"), value=nationality)
                        if _is_admin:
                            e_role = st.selectbox(
                                t("role"), ["member", "admin"],
                                index=0 if role == "member" else 1,
                            )
                        else:
                            e_role = role
                    e_pw = st.text_input(t("new_password"), type="password",
                                         help=t("new_password_hint"))
                    e_pw2 = st.text_input(t("confirm_password"), type="password")

                    if _is_admin:
                        sc1, sc2, sc3 = st.columns(3)
                    else:
                        sc1, sc2 = st.columns(2)

                    with sc1:
                        save = st.form_submit_button(t("save"), use_container_width=True)
                    with sc2:
                        cancel = st.form_submit_button(t("cancel"), use_container_width=True)
                    if _is_admin:
                        with sc3:
                            delete_btn = st.form_submit_button(
                                f"🗑 {t('delete')}", use_container_width=True
                            )
                    else:
                        delete_btn = False

                    if save:
                        if e_pw and e_pw != e_pw2:
                            st.error(t("password_mismatch"))
                        else:
                            update_data = {
                                "name": e_name, "room": e_room, "phone": e_phone,
                                "email": e_email, "role": e_role, "join_date": e_join,
                                "gender": e_gender, "nationality": e_nationality,
                            }
                            if e_pw:
                                update_data["password"] = hash_password(e_pw)
                            try:
                                update_member(member_id, update_data)
                                st.success(t("member_updated"))
                                del st.session_state[f"editing_{member_id}"]
                                st.rerun()
                            except Exception as e:
                                st.error(f"{t('error')}: {e}")

                    if cancel:
                        del st.session_state[f"editing_{member_id}"]
                        st.rerun()

                    if delete_btn:
                        try:
                            delete_member(member_id)
                            st.success(t("member_deleted"))
                            del st.session_state[f"editing_{member_id}"]
                            st.rerun()
                        except Exception as e:
                            st.error(f"{t('error')}: {e}")
