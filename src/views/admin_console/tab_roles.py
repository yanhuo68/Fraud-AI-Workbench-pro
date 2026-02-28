import streamlit as st
import requests

def render_roles_tab(API_URL, headers):
    st.header("🎭 Role Management")
    st.info("Define roles and their mapped page permissions. Changes here affect the sidebar and page access instantly.")
    
    # 1. Create Role
    with st.expander("➕ Create New Role"):
        with st.form("create_role_form"):
            new_role_name = st.text_input("Role Name", placeholder="e.g. Data Scientist")
            st.form_submit_button("Create Role")
            # Note: Permissions added via edit later for simplicity or could be here
            if _ := st.session_state.get("create_role_btn_submit"): # dummy
                pass
        
        # Simple create if name entered
        if st.button("Confirm Create Role", key="confirm_role"):
            if new_role_name:
                try:
                    resp = requests.post(f"{API_URL}/admin/roles", json={"name": new_role_name, "permissions": ["home"]}, headers=headers)
                    if resp.status_code == 200:
                        st.success(f"Role '{new_role_name}' created!")
                        st.rerun()
                    else:
                        st.error(resp.text)
                except Exception as e:
                    st.error(f"Error: {e}")

    # 2. List & Edit Roles
    try:
        resp = requests.get(f"{API_URL}/admin/roles", headers=headers)
        if resp.status_code == 200:
            roles_data = resp.json().get("roles", [])
            
            # Master list of pages for checkboxes
            all_pages = [
                "1_📁_Data_Hub", "2_🧠_SQL_RAG_Assistant", "3_🕸️_Graph_RAG_Assistant", 
                "4_🎥_Multimodal_RAG_Assistant", "5_📈_Trends_and_Insights", "6_🔄_ML_Workflow", 
                "9_🧠_LLM_Fine_Tuning", "10_🔌_API_Interaction", "11_🛡️_Admin_Console"
            ]

            for r in roles_data:
                r_name = r["name"]
                with st.expander(f"🎭 Role: **{r_name}**"):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.markdown("**Permissions (Allowed Pages):**")
                        current_perms = r["permissions"]
                        
                        # Use checkboxes for permissions
                        new_perms = []
                        for pg in all_pages:
                            if st.checkbox(pg, value=(pg in current_perms), key=f"cb_{r_name}_{pg}"):
                                new_perms.append(pg)
                    
                    with c2:
                        if st.button("💾 Save Permissions", key=f"save_r_{r_name}"):
                            try:
                                sresp = requests.post(f"{API_URL}/admin/roles", json={"name": r_name, "permissions": new_perms}, headers=headers)
                                if sresp.status_code == 200:
                                    st.success("Saved!")
                                    # Clear cached perms if it's the current user's role
                                    if st.session_state.user.get("role") == r_name:
                                        st.session_state.user_permissions = None
                                    st.rerun()
                                else:
                                    st.error("Failed to save")
                            except Exception as e:
                                st.error(str(e))
                        
                        if r_name not in ["admin", "guest"]:
                            if st.button("🗑️ Delete Role", key=f"del_r_{r_name}"):
                                try:
                                    dresp = requests.delete(f"{API_URL}/admin/roles/{r_name}", headers=headers)
                                    if dresp.status_code == 200:
                                        st.success("Deleted")
                                        st.rerun()
                                    else:
                                        st.error("Failed")
                                except Exception as e:
                                    st.error(str(e))
        else:
            st.error("Failed to fetch roles.")
    except Exception as e:
        st.error(f"Error: {e}")
