import streamlit as st
import pandas as pd
import altair as alt
import io
import os
import datetime
from pathlib import Path
from agents.eda_agent import compute_basic_eda, eda_narrative
from agents.fraud_risk_agent import add_fraud_risk_score
from agents.pandas_agent import query_dataframe, generate_suggested_questions
from agents.llm_router import init_llm
from utils.pdf_gen import create_trends_report

def render_structured_analysis(df: pd.DataFrame):
    display_source = st.session_state.get('analysis_source', 'Unknown Source')
    st.markdown(f"**Current Dataset:** `{display_source}` ({len(df)} rows)")
    
    with st.expander("📄 View Data Sample"):
        st.dataframe(df.head())
        st.caption("Debug Info (Column Types):")
        st.write(df.dtypes.astype(str))

    _csv_buf = io.StringIO()
    df.to_csv(_csv_buf, index=False)
    _exp_c1, _exp_c2 = st.columns([1, 5])
    _exp_c1.download_button(
        label="⬇ Export CSV",
        data=_csv_buf.getvalue(),
        file_name="trends_dataset.csv",
        mime="text/csv",
        help="Download the full working dataset as CSV"
    )
    _exp_c2.caption(f"{len(df):,} rows · {len(df.columns)} columns")

    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    time_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c]) or any(x in c.lower() for x in ['date', 'time', 'created', 'seen', 'timestamp'])]
    
    st.subheader("📊 Trend Analysis")
    if time_cols:
        c1, c2, c3 = st.columns(3)
        y_col = c1.selectbox("Metric (Y-axis):", df.columns)
        x_col = c2.selectbox("Time (X-axis):", time_cols)
        agg_period = c3.radio(
            "Group by period:",
            ["None (raw)", "Day", "Week", "Month"],
            horizontal=True,
            help="Aggregate values into time buckets for cleaner charts"
        )

        if st.button("Generate Trend Chart"):
            try:
                df_plot = df.copy()
                df_plot[x_col] = pd.to_datetime(df_plot[x_col], errors='coerce')
                df_plot = df_plot.dropna(subset=[x_col]).sort_values(by=x_col)

                if agg_period != "None (raw)" and pd.api.types.is_numeric_dtype(df_plot[y_col]):
                    freq_map = {"Day": "D", "Week": "W", "Month": "ME"}
                    freq = freq_map[agg_period]
                    df_plot = (
                        df_plot.set_index(x_col)[[y_col]]
                        .resample(freq).mean()
                        .reset_index()
                    )

                st.session_state.trend_active = True
                st.session_state.trend_df = df_plot[[x_col, y_col]].to_dict('records')
                st.session_state.trend_x = x_col
                st.session_state.trend_y = y_col
                st.session_state.trend_agg = agg_period

                if 'trend_insights' in st.session_state:
                    del st.session_state.trend_insights

            except Exception as e:
                st.error(f"Trend plot setup failed: {e}")

        if st.session_state.get('trend_active') and 'trend_df' in st.session_state:
            try:
                chart_df = pd.DataFrame(st.session_state.trend_df)
                t_x = st.session_state.trend_x
                t_y = st.session_state.trend_y
                agg_label = st.session_state.get('trend_agg', 'None (raw)')

                chart_df[t_x] = pd.to_datetime(chart_df[t_x])
                agg_suffix = f" (aggregated by {agg_label})" if agg_label != "None (raw)" else ""
                
                chart = alt.Chart(chart_df).mark_line(point=True).encode(
                    x=alt.X(t_x, title=f"Time ({t_x})"),
                    y=alt.Y(t_y, title=f"Metric ({t_y}){agg_suffix}"),
                    tooltip=[t_x, t_y]
                ).properties(
                    title=f"Trend of {t_y} over {t_x}{agg_suffix}"
                ).interactive()

                st.altair_chart(chart, use_container_width=True)
                
                if st.button("📝 Generate Trend Insights"):
                    with st.spinner("Analyzing trend..."):
                        stats_summary = chart_df[t_y].describe().to_string() if pd.api.types.is_numeric_dtype(chart_df[t_y]) else "Non-numeric data"
                        trend_desc = f"Data from {chart_df[t_x].min()} to {chart_df[t_x].max()}. Metric: {t_y}."
                        
                        llm_id = st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini")
                        llm = init_llm(llm_id)
                        prompt = (
                            f"Analyze this trend data summary.\n"
                            f"Context: {trend_desc}\n"
                            f"Stats:\n{stats_summary}\n\n"
                            f"Identify the overall direction, any obvious spikes (if visible from stats), and potential seasonality or anomalies. Keep it brief (3 bullets)."
                        )
                        response = llm.invoke(prompt)
                        st.session_state.trend_insights = response.content

                if 'trend_insights' in st.session_state:
                    st.info(st.session_state.trend_insights)
                    
            except Exception as e:
                st.error(f"Rendering trend failed: {e}")
    elif not numeric_cols:
        st.warning("No numeric columns found for plotting.")
    elif not time_cols:
        st.warning("No date/time columns found for trend plotting.")

    st.markdown("---")
    st.subheader("🔍 Automated EDA")
    
    if st.button("Generate EDA Report"):
        with st.spinner("Analyzing..."):
            eda_summary = compute_basic_eda(df)
            
            if eda_summary["numeric_summary"] is not None:
                st.caption("Numeric Stats")
                st.dataframe(eda_summary["numeric_summary"])
            
            eda_text = eda_narrative(
                df=df,
                question=f"Analyze trends and anomalies in this dataset ({st.session_state.analysis_source})",
                eda_summary=eda_summary,
                schema_text=f"Source: {st.session_state.analysis_source}",
                llm_id=st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini"),
            )
            st.markdown("### 🧠 AI Insights")
            st.markdown(eda_text)

    st.markdown("---")
    st.subheader("🧮 Fraud Risk Scoring")
    if st.button("Compute Risk Scores"):
        try:
            with st.spinner("Scoring..."):
                df_scored = add_fraud_risk_score(df)
                st.dataframe(df_scored.sort_values("fraud_risk_score", ascending=False).head(50))
                st.session_state.last_risk_stats = df_scored['fraud_risk_score'].describe().to_string()
        except Exception as e:
            st.error(f"Risk scoring failed: {e}")

    st.markdown("---")
    st.subheader("🤖 AI Investigator (Anomaly Detection)")
    st.info("Uses Unsupervised Learning (Isolation Forest) to find statistical outliers.")
    
    if st.button("Run AI Investigator"):
        with st.spinner("Training Model & Scanning Data..."):
            try:
                from agents.anomaly_agent import detect_anomalies
                df_anom = detect_anomalies(df, contamination=0.05)
                st.session_state.last_anomaly_df = df_anom
                if 'last_anomaly_analysis' in st.session_state:
                    del st.session_state.last_anomaly_analysis
            except Exception as e:
                st.error(f"AI Investigation Failed: {e}")

    if "last_anomaly_df" in st.session_state and st.session_state.last_anomaly_df is not None:
        try:
            df_anom = st.session_state.last_anomaly_df
            n_anom = len(df_anom[df_anom['anomaly_label'] == 'Anomaly'])
            st.metric("Anomalies Found", n_anom, f"{n_anom/len(df):.1%}")
            
            numeric_cols_anom = df_anom.select_dtypes(include="number").columns.tolist()
            if len(numeric_cols_anom) >= 2 or (time_cols and numeric_cols_anom):
                st.write("### 🔎 Anomaly Visualization")
                
                x_axis = time_cols[0] if time_cols else numeric_cols_anom[0]
                y_axis = numeric_cols_anom[0] if not time_cols else numeric_cols_anom[0]
                
                c1, c2 = st.columns(2)
                x_user = c1.selectbox("X-Axis", df_anom.columns, index=df_anom.columns.get_loc(x_axis) if x_axis in df_anom.columns else 0, key="anom_x")
                y_user = c2.selectbox("Y-Axis", numeric_cols_anom, index=0, key="anom_y")
                
                chart_anom = alt.Chart(df_anom).mark_circle(size=60).encode(
                    x=alt.X(x_user, title=x_user),
                    y=alt.Y(y_user, title=y_user),
                    color=alt.Color('anomaly_label', scale=alt.Scale(domain=['Normal', 'Anomaly'], range=['#3498db', '#e74c3c'])),
                    tooltip=df_anom.columns.tolist()
                ).interactive().properties(
                    title=f"Normal vs Anomalies ({y_user} by {x_user})"
                )
                st.altair_chart(chart_anom, use_container_width=True)
            
            st.write("### 🚨 Top Anomalies Detected")
            top_anomalies = df_anom[df_anom['anomaly_label'] == 'Anomaly'].sort_values('anomaly_score', ascending=True)
            st.dataframe(top_anomalies.head(50))

            _anom_buf = io.StringIO()
            top_anomalies.to_csv(_anom_buf, index=False)
            st.download_button(
                label="⬇ Export Anomalies CSV",
                data=_anom_buf.getvalue(),
                file_name="detected_anomalies.csv",
                mime="text/csv",
                help="Download all detected anomaly rows"
            )

            if st.button("📝 Generate AI Insights for Anomalies"):
                with st.spinner("Analyzing anomalies..."):
                    try:
                        stats_csv = top_anomalies.head(20).to_csv(index=False)
                        prompt = (
                            f"You are a Fraud Investigator. Analyze the following detected anomalies:\n"
                            f"{stats_csv}\n\n"
                            "Task: Identify common patterns among these anomalies (e.g. specific user, location, or high amounts). "
                            "Explain WHY these might be outliers compared to normal behavior. "
                            "Keep it under 150 words."
                        )

                        llm_id = st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini")
                        llm = init_llm(llm_id)
                        response = llm.invoke(prompt)
                        st.session_state.last_anomaly_analysis = response.content
                    except Exception as e:
                        st.error(f"Insight Generation Failed: {e}")

            if "last_anomaly_analysis" in st.session_state:
                st.info("### 🧠 AI Anomaly Analysis")
                st.markdown(st.session_state.last_anomaly_analysis)
            
        except Exception as e:
            st.error(f"Displaying Results Failed: {e}")

    st.markdown("---")
    st.subheader("🗺️ Geospatial Analysis (Top Locations)")
    
    loc_cols = [c for c in df.columns if 'country' in c.lower() or 'state' in c.lower() or 'city' in c.lower()]
    
    col1_geo, col2_geo = st.columns([3, 1])
    with col1_geo:
        all_cols = list(df.columns)
        prioritized_cols = loc_cols + [c for c in all_cols if c not in loc_cols]
        unique_cols = list(dict.fromkeys(prioritized_cols))
        
        geo_col = st.selectbox(
            "Select Location/Category Column:", 
            unique_cols, 
            index=0,
            help="Choose the column to group by (e.g., Country, State, City, or Category)."
        )

    with col2_geo:
        st.write("") 
        st.write("")
        gen_btn = st.button("Generate Chart", key="geo_gen_btn")

    if gen_btn:
        try:
            df_geo = df.copy()
            df_geo[geo_col] = df_geo[geo_col].astype(str).fillna("Unknown")
            
            agg_dict = {df.columns[0]: 'count'}
            title_text = "Transaction Volume"
            target_col_for_color = "Transaction_Count"
            
            if 'fraud_risk_score' in df.columns:
                agg_dict['fraud_risk_score'] = 'mean'
                title_text = "Avg Risk Score"
                target_col_for_color = "Avg_Risk_Score"
            
            geo_summary = df_geo.groupby(geo_col).agg(
                Transaction_Count=(df.columns[0], 'count'),
                Avg_Risk_Score=('fraud_risk_score', 'mean') if 'fraud_risk_score' in df.columns else (df.columns[0], 'count')
            ).reset_index()
            
            sort_metric = "Avg_Risk_Score" if 'fraud_risk_score' in df.columns else "Transaction_Count"
            geo_summary = geo_summary.sort_values(sort_metric, ascending=False).head(20)
            
            st.session_state.geo_summary = geo_summary
            st.session_state.geo_col_name = geo_col
            st.session_state.geo_title_text = title_text
            st.session_state.geo_sort_metric = sort_metric
            
            if 'last_location_analysis' in st.session_state:
                del st.session_state.last_location_analysis
                
        except Exception as e:
            st.error(f"Analysis Failed: {e}")

    if "geo_summary" in st.session_state:
        geo_summary = st.session_state.geo_summary
        final_geo_col_name = st.session_state.get('geo_col_name', 'Location')
        title_text = st.session_state.get('geo_title_text', 'Value')
        sort_metric = st.session_state.get('geo_sort_metric', 'Transaction_Count')
        
        chart_geo = alt.Chart(geo_summary).mark_bar().encode(
            x=alt.X(f'{sort_metric}:Q', title=title_text),
            y=alt.Y(f'{final_geo_col_name}:N', sort='-x', title=final_geo_col_name),
            color=alt.Color(f'{sort_metric}:Q', scale=alt.Scale(scheme='reds'), legend=None),
            tooltip=[
                alt.Tooltip(f'{final_geo_col_name}:N', title=final_geo_col_name),
                alt.Tooltip(f'{sort_metric}:Q', title=title_text, format=',.2f'),
                alt.Tooltip('Transaction_Count:Q', title='Count')
            ]
        ).properties(
            width=700,
            height=max(350, 25 * len(geo_summary)), 
            title=f"Top {len(geo_summary)} by {title_text}"
        ).interactive()
        
        st.altair_chart(chart_geo, use_container_width=True)
        st.write("### 📍 Statistics Table")
        st.dataframe(geo_summary)
        
        if st.button("📝 Generate AI Insights for Locations"):
            with st.spinner("Analyzing location patterns..."):
                try:
                    stats_csv = geo_summary.to_csv(index=False)
                    prompt = (
                        f"You are a Fraud Intelligence Analyst. Analyze the following statistics:\n"
                        f"{stats_csv}\n\n"
                        f"Metric: {title_text}\n"
                        f"Grouping: {final_geo_col_name}\n"
                        "Provide a brief, high-level summary of the risk patterns. "
                        "Identify which groups have the highest risk/volume and suggest where to focus investigation. "
                        "Keep it under 150 words."
                    )
                    
                    llm_id = st.session_state.get("llm_settings", {}).get("selected_llm", "openai:gpt-4o-mini")
                    llm = init_llm(llm_id)
                    response = llm.invoke(prompt)
                    
                    st.session_state.last_location_analysis = response.content
                    
                except Exception as e:
                    st.error(f"Insight Generation Failed: {e}")
        
        if "last_location_analysis" in st.session_state:
            st.info("### 🧠 AI Analysis")
            st.markdown(st.session_state.last_location_analysis)

    st.markdown("---")
    st.subheader("📄 Export Report")
    
    report_opts_col1, report_opts_col2 = st.columns([3, 1])
    with report_opts_col1:
        custom_out_dir = st.text_input("Save Report To (Folder Path):", value="data/generated")
    
    if st.button("Generate PDF Report"):
        with st.spinner("Generating Report..."):
            try:
                sections = []
                chart_path = None
                if numeric_cols and time_cols:
                    try:
                        import matplotlib.pyplot as plt
                        plt.figure(figsize=(10, 6))
                        time_c = time_cols[0]
                        num_c = numeric_cols[0]
                        
                        df_chart = df.copy()
                        df_chart[time_c] = pd.to_datetime(df_chart[time_c], errors='coerce')
                        df_chart = df_chart.dropna(subset=[time_c]).sort_values(by=time_c)
                        
                        plt.plot(df_chart[time_c], df_chart[num_c])
                        plt.title(f"Trend: {num_c} over {time_c}")
                        plt.xlabel(time_c)
                        plt.ylabel(num_c)
                        plt.grid(True)
                        
                        chart_path = "data/generated/trend_chart.png"
                        os.makedirs("data/generated", exist_ok=True)
                        plt.savefig(chart_path)
                        plt.close()
                        
                        sections.append({
                            "title": "Trend Visualization",
                            "image": chart_path
                        })
                    except Exception as e:
                        st.warning(f"Could not generate chart image for report: {e}")

                summary = f"Dataset contains {len(df)} rows.\nColumns: {', '.join(df.columns)}"
                if "analysis_source" in st.session_state:
                    summary += f"\nSource: {st.session_state.analysis_source}"
                
                sections.append({
                    "title": "Dataset Summary",
                    "content": summary
                })
                
                if "last_risk_stats" in st.session_state:
                     sections.append({
                        "title": "Risk Analysis Stats",
                        "content": st.session_state.last_risk_stats
                    })

                out_dir = Path(custom_out_dir)
                out_dir.mkdir(parents=True, exist_ok=True)
                report_filename = f"report_{len(df)}_rows_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
                report_path = str(out_dir / report_filename)
                
                create_trends_report(
                    source_name=st.session_state.analysis_source,
                    sections=sections,
                    output_path=report_path
                )
                
                st.success(f"Report saved to: `{report_path}`")
                with open(report_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=report_filename)
                    
            except Exception as e:
                st.error(f"Report Generation Failed: {e}")


    st.markdown("---")
    st.subheader("💬 Chat with Data")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if "suggested_questions" not in st.session_state:
        st.session_state.suggested_questions = []

    if df is not None and not st.session_state.suggested_questions:
        with st.spinner("Generating sample questions..."):
            st.session_state.suggested_questions = generate_suggested_questions(df)

    for role, content in st.session_state.chat_history:
        with st.chat_message(role):
            if role == "assistant" and isinstance(content, (pd.DataFrame, pd.Series)):
                st.dataframe(content)
            else:
                st.write(content)

    if st.session_state.suggested_questions:
        st.write("Need inspiration? Try these:")
        cols = st.columns(len(st.session_state.suggested_questions))
        for i, q in enumerate(st.session_state.suggested_questions):
            if cols[i].button(q, key=f"sugg_{i}"):
                st.session_state.chat_history.append(("user", q))
                st.session_state.processing_prompt = q
                st.rerun()

    prompt = st.chat_input("Ask a question about this data...")
    final_prompt = None
    if prompt:
        final_prompt = prompt
    elif "processing_prompt" in st.session_state and st.session_state.processing_prompt:
        final_prompt = st.session_state.processing_prompt
        del st.session_state.processing_prompt

    if final_prompt:
        if not prompt: 
            pass
        else:
            st.session_state.chat_history.append(("user", final_prompt))
            with st.chat_message("user"):
                st.write(final_prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = query_dataframe(df, final_prompt)
                if isinstance(response, (pd.DataFrame, pd.Series)):
                    st.dataframe(response)
                else:
                    st.code(response) if "Error" in str(response) else st.write(response)
                st.session_state.chat_history.append(("assistant", response))

    if st.session_state.get("chat_history"):
        if st.button("🗑 Clear Chat History", key="clear_data_chat"):
            st.session_state.chat_history = []
            st.rerun()
