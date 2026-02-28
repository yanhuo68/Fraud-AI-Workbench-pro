import streamlit as st
import pandas as pd
import json
from pathlib import Path
from utils.version_manager import DatasetManager

def render_review_tab(dataset_mgr: DatasetManager):
    st.header("Dataset Review 📊")
    st.caption("Review your collected training examples")
    
    st.markdown("---")
    st.subheader("📂 Dataset Management")
    
    col_dm1, col_dm2, col_dm3, col_dm4 = st.columns([3, 1, 1, 1])
    
    with col_dm1:
        all_datasets = dataset_mgr.get_all_datasets()
        active_dataset_id = dataset_mgr.get_active_dataset()
        
        if all_datasets:
            for ds in all_datasets:
                dataset_mgr._update_sample_count(ds['id'])
            all_datasets = dataset_mgr.get_all_datasets()
            dataset_options = {f"{ds['name']} ({ds['sample_count']} samples)": ds['id'] for ds in all_datasets}
            current_name = next((k for k, v in dataset_options.items() if v == active_dataset_id), list(dataset_options.keys())[0])
            
            selected_display = st.selectbox(
                "📁 Select Dataset",
                options=list(dataset_options.keys()),
                index=list(dataset_options.keys()).index(current_name) if current_name in dataset_options else 0
            )
            
            selected_dataset_id = dataset_options[selected_display]
            if selected_dataset_id != active_dataset_id:
                dataset_mgr.set_active_dataset(selected_dataset_id)
                st.rerun()
        else:
            st.warning("⚠️ No datasets found")
            st.stop()
    
    with col_dm2:
        if st.button("✏️ Rename", use_container_width=True):
            st.session_state['show_rename'] = True
    
    with col_dm3:
        if st.button("📋 Clone", use_container_width=True):
            st.session_state['show_clone'] = True
    
    with col_dm4:
        if st.button("🗑️ Delete", use_container_width=True, type="secondary"):
            st.session_state['show_delete_dataset'] = True
    
    if st.session_state.get('show_rename', False):
        with st.expander("✏️ Rename Dataset", expanded=True):
            current_ds = dataset_mgr.get_dataset(selected_dataset_id)
            new_name = st.text_input("New name", value=current_ds['name'])
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                if st.button("✅ Save", key="rename_save", use_container_width=True):
                    info_file = Path(f"data/llm/datasets/{selected_dataset_id}/info.json")
                    with open(info_file, 'r') as f: info = json.load(f)
                    info['name'] = new_name
                    with open(info_file, 'w') as f: json.dump(info, f, indent=2)
                    
                    metadata = dataset_mgr._load_metadata()
                    for ds in metadata['datasets']:
                        if ds['id'] == selected_dataset_id: ds['name'] = new_name; break
                    dataset_mgr._save_metadata(metadata)
                    
                    st.success(f"✅ Renamed to: {new_name}")
                    st.session_state['show_rename'] = False
                    st.rerun()
            with col_r2:
                if st.button("❌ Cancel", key="rename_cancel", use_container_width=True):
                    st.session_state['show_rename'] = False
                    st.rerun()
    
    if st.session_state.get('show_clone', False):
        with st.expander("📋 Clone Dataset", expanded=True):
            current_ds = dataset_mgr.get_dataset(selected_dataset_id)
            clone_name = st.text_input("New dataset name", placeholder=f"{current_ds['name']} (Copy)")
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                if st.button("✅ Clone", key="clone_save", use_container_width=True):
                    if clone_name:
                        try:
                            new_id = dataset_mgr.create_dataset(name=clone_name, description=f"Cloned from {current_ds['name']}", clone_from=selected_dataset_id)
                            st.success(f"✅ Cloned to: {clone_name}")
                            dataset_mgr.set_active_dataset(new_id)
                            st.session_state['show_clone'] = False
                            st.rerun()
                        except Exception as e: st.error(f"❌ Error: {e}")
            with col_c2:
                if st.button("❌ Cancel", key="clone_cancel", use_container_width=True):
                    st.session_state['show_clone'] = False
                    st.rerun()
    
    if st.session_state.get('show_delete_dataset', False):
        with st.expander("⚠️ Delete Dataset", expanded=True):
            st.warning(f"Are you sure you want to delete '{dataset_mgr.get_dataset(selected_dataset_id)['name']}'?")
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                if st.button("❌ Delete Permanently", key="delete_confirm", type="secondary", use_container_width=True):
                    if len(all_datasets) > 1:
                        dataset_mgr.delete_dataset(selected_dataset_id)
                        st.success("✅ Dataset deleted")
                        st.session_state['show_delete_dataset'] = False
                        st.rerun()
                    else: st.error("Cannot delete the last dataset")
            with col_d2:
                if st.button("✅ Keep Dataset", key="delete_cancel", use_container_width=True):
                    st.session_state['show_delete_dataset'] = False
                    st.rerun()
    
    st.markdown("---")
    examples = dataset_mgr.get_samples(selected_dataset_id)
    if not examples:
        st.warning("Dataset is empty!")
        st.stop()
    st.success(f"✅ Loaded {len(examples)} examples from '{dataset_mgr.get_dataset(selected_dataset_id)['name']}'")
    
    col1, col2, col3 = st.columns(3)
    categories = [ex.get('category', 'Unknown') for ex in examples]
    cat_counts = pd.Series(categories).value_counts()
    with col1: st.metric("Total", len(examples))
    with col2: st.metric("Categories", len(cat_counts))
    with col3:
        avg = sum(len(ex.get('output', '')) for ex in examples) / len(examples)
        st.metric("Avg Length", f"{avg:.0f}")

    import altair as _alt2
    _chart_c1, _chart_c2 = st.columns(2)
    with _chart_c1:
        _cat_df = cat_counts.reset_index()
        _cat_df.columns = ['Category', 'Count']
        _cat_chart = _alt2.Chart(_cat_df).mark_bar(color='#3498db').encode(
            x=_alt2.X('Count:Q', title='Samples'),
            y=_alt2.Y('Category:N', sort='-x', title=''),
            tooltip=['Category', 'Count']
        ).properties(title='Fraud Categories', height=150)
        st.altair_chart(_cat_chart, use_container_width=True)
    with _chart_c2:
        _ratings_ds = pd.Series([e.get('rating', 'Unknown') for e in examples]).value_counts().reset_index()
        _ratings_ds.columns = ['Rating', 'Count']
        _color_map2 = {'Excellent': '#2ecc71', 'Good': '#3498db', 'Fair': '#f39c12', 'Poor': '#e74c3c', 'Unknown': '#95a5a6'}
        _ratings_ds['Color'] = _ratings_ds['Rating'].map(_color_map2).fillna('#95a5a6')
        _rat_chart = _alt2.Chart(_ratings_ds).mark_bar().encode(
            x=_alt2.X('Count:Q', title='Samples'),
            y=_alt2.Y('Rating:N', sort=None, title=''),
            color=_alt2.Color('Color:N', scale=None, legend=None),
            tooltip=['Rating', 'Count']
        ).properties(title='Quality Ratings', height=150)
        st.altair_chart(_rat_chart, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📋 Sample Management")
    st.caption("Click sample to expand • Edit to make changes • Delete unwanted samples")
    for idx, ex in enumerate(examples[:15]):
        with st.expander(f"#{idx+1}: {ex.get('category', 'Unknown')} - {ex.get('rating', 'N/A')}"):
            col_v1, col_v2 = st.columns([8, 2])
            with col_v1:
                st.text(f"Category: {ex.get('category', 'N/A')}")
                st.text(f"Rating: {ex.get('rating', 'N/A')}")
            with col_v2:
                if st.button("🗑️ Delete", key=f"del_{idx}", use_container_width=True, type="secondary"):
                    dataset_mgr.delete_sample(selected_dataset_id, idx)
                    st.success("✅ Deleted!")
                    st.rerun()
            st.code(ex.get('input', 'N/A'), language="text")
            st.text_area("Expert Analysis", ex.get('output', 'N/A'), height=100, disabled=True, key=f"out_{idx}")
    
    if len(examples) > 15: st.info(f"Showing first 15 of {len(examples)}")
    
    st.markdown("---")
    st.subheader("💾 Export Dataset")
    col_exp1, col_exp2 = st.columns(2)
    with col_exp1:
        st.markdown("**Browser Download** (📁 ~/Downloads/)")
        st.download_button("📥 Download JSON", json.dumps(examples, indent=2), "dataset.json", use_container_width=True)
        st.caption("For manual review/sharing")
    with col_exp2:
        st.markdown("**Save to Project** (📂 data/llm/)")
        if st.button("💾 Save to Project Folder", use_container_width=True):
            project_path = "data/llm/dataset_raw.json"
            Path("data/llm").mkdir(parents=True, exist_ok=True)
            with open(project_path, 'w') as f: json.dump(examples, f, indent=2)
            st.success(f"✅ Saved {len(examples)} examples to {project_path}")
            st.info("🎯 Raw dataset saved for review/backup!")
        st.caption("Full data with all fields")
