import streamlit as st
import requests

def render_users_tab(API_URL, headers):
    st.header("User Management")
    st.info("Directly manage application users and their access roles.")

    # ── NEW: search box ────────────────────────────────────────────────────────
    _user_search = st.text_input("🔍 Search users", placeholder="Filter by username or role…", key="user_search")

    try:
        resp = requests.get(f"{API_URL}/admin/users", headers=headers)
        if resp.status_code == 200:
            users_list = resp.json().get("users", [])

            # ── NEW: apply search filter ───────────────────────────────────────
            if _user_search:
                _q = _user_search.lower()
                users_list = [u for u in users_list if _q in u.get('username', '').lower() or _q in u.get('role', '').lower()]

            if not users_list:
                st.info("No users found." if not _user_search else f"No users matching '{_user_search}'.")
            else:
                # ── NEW: summary header ────────────────────────────────────────
                _role_counts = {}
                for _u in users_list:
                    _role_counts[_u.get('role', 'unknown')] = _role_counts.get(_u.get('role', 'unknown'), 0) + 1
                _summary = " · ".join([f"**{v}** {k}" for k, v in _role_counts.items()])
                st.caption(f"Showing {len(users_list)} user(s): {_summary}")
                # Column Headers
                header_cols = st.columns([1, 2, 2, 2, 1.5, 1])
                header_cols[0].markdown("**ID**")
                header_cols[1].markdown("**Username**")
                header_cols[2].markdown("**Email**") # New Column
                header_cols[3].markdown("**Role**")
                header_cols[4].markdown("**Security**")
                header_cols[5].markdown("**Delete**")
                st.markdown("---")

                # Fetch roles for the dropdown
                available_roles = ["admin", "guest"]
                try:
                    r_resp = requests.get(f"{API_URL}/admin/roles", headers=headers)
                    if r_resp.status_code == 200:
                        available_roles = [r["name"] for r in r_resp.json().get("roles", [])]
                except:
                    pass

                for u in users_list:
                    with st.container():
                        c_id, c_user, c_email, c_role, c_sec, c_del = st.columns([1, 2, 2, 2, 1.5, 1])
                        
                        with c_id:
                            st.write(f"{u['id']}")
                        
                        with c_user:
                            # Rename Popover
                            with st.popover(f"✏️ {u['username']}", width="stretch"):
                                new_name = st.text_input("New Username", value=u['username'], key=f"name_in_{u['id']}")
                                if st.button("Update Username", key=f"name_btn_{u['id']}"):
                                    try:
                                        resp = requests.patch(
                                            f"{API_URL}/admin/users/{u['id']}/username",
                                            json={"username": new_name},
                                            headers=headers
                                        )
                                        if resp.status_code == 200:
                                            st.success("Renamed")
                                            st.rerun()
                                        else:
                                            st.error(resp.json().get("detail", "Failed"))
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                        
                        with c_email:
                            email_val = u.get("email") or ""
                            # Email Update Popover
                            with st.popover(f"📧 {email_val if email_val else 'Set Email'}", width="stretch"):
                                new_email = st.text_input("New Email", value=email_val, key=f"email_in_{u['id']}")
                                if st.button("Update Email", key=f"email_btn_{u['id']}"):
                                    try:
                                        resp = requests.patch(
                                            f"{API_URL}/admin/users/{u['id']}/email",
                                            json={"email": new_email},
                                            headers=headers
                                        )
                                        if resp.status_code == 200:
                                            st.success("Email Updated")
                                            st.rerun()
                                        else:
                                            st.error(resp.json().get("detail", "Failed"))
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                        
                        with c_role:
                            # Role Change
                            new_role = st.selectbox(
                                "Role", 
                                available_roles, 
                                index=available_roles.index(u["role"]) if u["role"] in available_roles else 0,
                                key=f"role_sel_{u['id']}",
                                label_visibility="collapsed"
                            )
                            if new_role != u["role"]:
                                if st.button("Update Role", key=f"up_role_{u['id']}"):
                                    try:
                                        uresp = requests.patch(
                                            f"{API_URL}/admin/users/{u['id']}", 
                                            json={"role": new_role}, 
                                            headers=headers
                                        )
                                        if uresp.status_code == 200:
                                            st.success("Updated")
                                            st.rerun()
                                        else:
                                            st.error("Failed")
                                    except Exception:
                                        st.error("Error")
                        
                        with c_sec:
                            # Reset Password Popover
                            with st.popover("🔑 Reset", width="stretch"):
                                new_pw = st.text_input("New Password", type="password", key=f"pw_in_{u['id']}")
                                if st.button("Reset Password", key=f"pw_btn_{u['id']}"):
                                    try:
                                        resp = requests.patch(
                                            f"{API_URL}/admin/users/{u['id']}/password",
                                            json={"password": new_pw},
                                            headers=headers
                                        )
                                        if resp.status_code == 200:
                                            st.success("Password Reset")
                                        else:
                                            st.error(resp.json().get("detail", "Failed"))
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                        
                        with c_del:
                            if st.button("🗑️", key=f"del_user_{u['id']}"):
                                try:
                                    dresp = requests.delete(f"{API_URL}/admin/users/{u['id']}", headers=headers)
                                    if dresp.status_code == 200:
                                        st.success("Deleted")
                                        st.rerun()
                                    else:
                                        st.error("Failed")
                                except Exception:
                                    st.error("Error")
                        st.markdown("---")
        else:
            st.error(f"Failed to fetch users: {resp.text}")
    except Exception as e:
        st.error(f"Error fetching users: {e}")
