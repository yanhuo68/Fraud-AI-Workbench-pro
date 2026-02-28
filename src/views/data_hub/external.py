import streamlit as st
from views.data_hub.utils import auto_rebuild

def render_external_tab():
    st.header("🌍 External Data Connectors")
    st.info("Download datasets directly from Kaggle or GitHub. Files will be saved in your uploads folder for chat and execution.")
    
    col_k, col_g = st.columns(2)
    
    with col_k:
        st.subheader("🔵 Kaggle Dataset")
        st.caption("Requires KAGGLE_USERNAME and KAGGLE_KEY in Admin Console.")
        k_slug = st.text_input("Dataset Slug", placeholder="e.g., mlg-ulb/creditcardfraud")
        if st.button("📥 Download from Kaggle"):
            if not k_slug:
                st.warning("Please enter a dataset slug.")
            else:
                from utils.external_data import download_kaggle_dataset
                with st.spinner(f"Downloading {k_slug}..."):
                    res = download_kaggle_dataset(k_slug)
                    if res.get("success"):
                        st.success(f"Successfully downloaded {len(res.get('files', []))} files!")
                        with st.expander("Show files"):
                            st.write(res.get("files"))
                        if auto_rebuild():
                            st.balloons()
                            st.info("Friend message: Kaggle data imported, and both Graph Store & Knowledge Base have been rebuilt successfully!")
                    else:
                        st.error(f"Failed: {res.get('error')}")

    with col_g:
        st.subheader("🐙 GitHub Repository")
        st.caption("Downloads the default branch as a ZIP.")
        g_url = st.text_input("Repository URL", placeholder="e.g., https://github.com/pandas-dev/pandas")
        if st.button("📥 Download from GitHub"):
            if not g_url:
                st.warning("Please enter a repository URL.")
            else:
                from utils.external_data import download_github_repo
                with st.spinner(f"Downloading from {g_url}..."):
                    res = download_github_repo(g_url)
                    if res.get("success"):
                        st.success(f"Successfully downloaded {len(res.get('files', []))} files!")
                        with st.expander("Show files"):
                            st.write(res.get("files"))
                        if auto_rebuild():
                            st.balloons()
                            st.info("Friend message: GitHub data imported, and both Graph Store & Knowledge Base have been rebuilt successfully!")
                    else:
                        st.error(f"Failed: {res.get('error')}")
