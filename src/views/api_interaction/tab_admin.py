import streamlit as st
import json
from views.api_interaction.helpers import make_request, _ep

def render_admin_tab(api_base_url):
    adm_tabs = st.tabs(["👥 User Management", "🎭 Role & Permissions", "🗄️ Storage & Graph"])

    # ── User Management ────────────────────────────────────────────────────────
    with adm_tabs[0]:
        col_u1, col_u2 = st.columns(2)
        with col_u1:
            _ep("GET", "/admin/users", "admin")
            st.caption("List all registered users.")
            if st.button("List All Users", use_container_width=True, key="admin_users"):
                make_request("GET", "/admin/users", api_base_url)

            st.divider()
            _ep("DELETE", "/admin/users/{id}", "admin")
            st.caption("Permanently delete a user account.")
            d_uid = st.number_input("User ID to Delete", min_value=1, step=1, key="del_uid")
            if st.button("🗑 Delete User", use_container_width=True, key="del_user_btn", type="secondary"):
                make_request("DELETE", f"/admin/users/{d_uid}", api_base_url)

        with col_u2:
            _ep("PATCH", "/admin/users/{id}", "admin")
            st.caption("Update user role.")
            with st.form("patch_role_form"):
                pr_uid  = st.number_input("User ID", min_value=1, step=1, key="pr_uid")
                pr_role = st.selectbox("New Role", ["guest", "data_scientist", "admin"], key="pr_role")
                if st.form_submit_button("Update Role", use_container_width=True):
                    make_request("PATCH", f"/admin/users/{pr_uid}", api_base_url, payload={"role": pr_role})

            _ep("PATCH", "/admin/users/{id}/email", "admin")
            st.caption("Update user email.")
            with st.form("patch_email_form"):
                pe_uid   = st.number_input("User ID", min_value=1, step=1, key="pe_uid")
                pe_email = st.text_input("New Email")
                if st.form_submit_button("Update Email", use_container_width=True):
                    make_request("PATCH", f"/admin/users/{pe_uid}/email", api_base_url, payload={"email": pe_email})

            _ep("PATCH", "/admin/users/{id}/username", "admin")
            st.caption("Update username.")
            with st.form("patch_uname_form"):
                pu_uid  = st.number_input("User ID", min_value=1, step=1, key="pu_uid")
                pu_name = st.text_input("New Username")
                if st.form_submit_button("Update Username", use_container_width=True):
                    make_request("PATCH", f"/admin/users/{pu_uid}/username", api_base_url, payload={"username": pu_name})

            _ep("PATCH", "/admin/users/{id}/password", "admin")
            st.caption("Admin-force reset user password.")
            with st.form("patch_pw_form"):
                pp_uid = st.number_input("User ID", min_value=1, step=1, key="pp_uid")
                pp_pw  = st.text_input("New Password (min 8 chars)", type="password")
                if st.form_submit_button("Reset Password", use_container_width=True):
                    make_request("PATCH", f"/admin/users/{pp_uid}/password", api_base_url, payload={"new_password": pp_pw})

    # ── Roles & Permissions ────────────────────────────────────────────────────
    with adm_tabs[1]:
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            _ep("GET", "/admin/permissions")
            st.caption("Get current user's page permissions (uses Bearer token).")
            if st.button("Get My Permissions", use_container_width=True, key="get_perms"):
                make_request("GET", "/admin/permissions", api_base_url)

            st.divider()
            _ep("GET", "/admin/roles", "admin")
            st.caption("List all roles and their page permissions.")
            if st.button("List All Roles", use_container_width=True, key="list_roles"):
                make_request("GET", "/admin/roles", api_base_url)

        with col_r2:
            _ep("POST", "/admin/roles", "admin")
            st.caption("Create or update a role with specific page permissions.")
            with st.expander("📌 Request Schema"):
                st.code(json.dumps({
                    "name": "string — role name (e.g. analyst)",
                    "pages": ["page_id_1", "page_id_2"]
                }, indent=2), language="json")
            with st.form("create_role_form"):
                cr_name  = st.text_input("Role Name", placeholder="e.g. analyst")
                cr_pages = st.text_area("Pages (JSON array)", value='["1_📁_Data_Hub", "2_🧠_SQL_RAG_Assistant"]')
                if st.form_submit_button("Create/Update Role", use_container_width=True):
                    try:
                        make_request("POST", "/admin/roles", api_base_url, payload={"name": cr_name, "pages": json.loads(cr_pages)})
                    except Exception:
                        st.error("Invalid JSON in pages list.")

            st.divider()
            _ep("DELETE", "/admin/roles/{name}", "admin")
            st.caption("Delete a role by name.")
            dr_name = st.text_input("Role Name to Delete", placeholder="e.g. analyst", key="del_role_name")
            if st.button("🗑 Delete Role", use_container_width=True, key="del_role_btn", type="secondary"):
                if dr_name.strip():
                    make_request("DELETE", f"/admin/roles/{dr_name}", api_base_url)
                else:
                    st.warning("Enter a role name.")

    # ── Storage & Graph ────────────────────────────────────────────────────────
    with adm_tabs[2]:
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("##### 🗄️ Database Operations")
            _ep("POST", "/admin/clean-db", "admin")
            st.caption("⚠️ Drop all SQL tables and reset the database.")
            if st.button("🧹 Clean Database", use_container_width=True, key="clean_db", type="secondary"):
                make_request("POST", "/admin/clean-db", api_base_url)

            st.divider()
            _ep("POST", "/admin/delete-uploads", "admin")
            st.caption("⚠️ Delete all uploaded files and schema docs.")
            if st.button("🗑 Delete All Uploads", use_container_width=True, key="del_uploads", type="secondary"):
                make_request("POST", "/admin/delete-uploads", api_base_url)

        with col_g2:
            st.markdown("##### 🕸️ Graph Operations")
            _ep("GET", "/admin/graph-data", "auth")
            st.caption("Retrieve all nodes and relationships from the Graph Store.")
            if st.button("📊 Get Graph Data", use_container_width=True, key="get_graph"):
                make_request("GET", "/admin/graph-data", api_base_url)

            _ep("GET", "/admin/graph-evaluation", "auth")
            st.caption("Run a full graph health evaluation (connectivity, quality score).")
            if st.button("🔬 Evaluate Graph", use_container_width=True, key="eval_graph"):
                make_request("GET", "/admin/graph-evaluation", api_base_url)

            st.divider()
            _ep("POST", "/admin/rebuild-graph", "admin")
            st.caption("Rebuild the graph store from uploaded files.")
            if st.button("🔄 Rebuild Graph", use_container_width=True, key="rebuild_graph", type="primary"):
                make_request("POST", "/admin/rebuild-graph", api_base_url)

            _ep("POST", "/admin/project-data-to-graph", "admin")
            st.caption("Project SQL table data as nodes/edges into the graph store.")
            if st.button("📤 Project SQL → Graph", use_container_width=True, key="proj_graph", type="primary"):
                make_request("POST", "/admin/project-data-to-graph", api_base_url)

            _ep("POST", "/admin/delete-graph", "admin")
            st.caption("⚠️ Delete all graph nodes and relationships.")
            if st.button("🗑 Delete Graph", use_container_width=True, key="del_graph", type="secondary"):
                make_request("POST", "/admin/delete-graph", api_base_url)
