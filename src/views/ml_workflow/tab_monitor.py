import streamlit as st
import pandas as pd
import altair as alt
import os

def render_monitor_tab():
    st.header("Step 6: Monitor & Maintain Your Model 📊")
    st.info("Best practices for monitoring model performance and deciding when to retrain.")

    _hist_path = "data/ml/scoring_history.csv"
    if os.path.exists(_hist_path):
        try:
            _h = pd.read_csv(_hist_path, on_bad_lines='skip')
            if "timestamp" in _h.columns and "fraud_probability" in _h.columns:
                _h["timestamp"] = pd.to_datetime(_h["timestamp"], errors='coerce')
                _h = _h.dropna(subset=["timestamp"]).sort_values("timestamp")

                st.subheader("📈 6.0 Live Scoring History")
                _tcol1, _tcol2, _tcol3 = st.columns(3)
                _tcol1.metric("Total Scored", f"{len(_h):,}")
                _tcol2.metric("Avg Risk Score", f"{_h['fraud_probability'].mean():.3f}")
                _n_hi = (_h['fraud_probability'] >= 0.7).sum()
                _tcol3.metric("🔴 High Risk Flags", _n_hi)

                _hist_chart = alt.Chart(_h).mark_line(point=True, color='#e74c3c').encode(
                    x=alt.X("timestamp:T", title="Scored At"),
                    y=alt.Y("fraud_probability:Q", title="Fraud Probability", scale=alt.Scale(domain=[0, 1])),
                    tooltip=["timestamp:T", "fraud_probability:Q"]
                ).properties(
                    title="Fraud Probability Over Time (Scoring History)",
                    height=220
                ).interactive()

                _thresh_line = alt.Chart(pd.DataFrame({"y": [0.5]})).mark_rule(
                    color="orange", strokeWidth=1.5, strokeDash=[4, 4]
                ).encode(y="y:Q")

                st.altair_chart(_hist_chart + _thresh_line, use_container_width=True)
                st.caption("Orange dashed line = 0.5 decision threshold. Points above = predicted Fraud.")

                import io as _mio
                _mcsv = _mio.StringIO()
                _h.to_csv(_mcsv, index=False)
                st.download_button(
                    label="⬇ Download Scoring History CSV",
                    data=_mcsv.getvalue(),
                    file_name="scoring_history.csv",
                    mime="text/csv",
                    help="Full log of all scored transactions"
                )
                st.markdown("---")
        except Exception as _e:
            st.warning(f"Could not load scoring history: {_e}")

    st.subheader("6.1 🎯 Retrain Decision Tool")
    st.caption("Answer these questions to get a retrain recommendation")
    
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        days_since_train = st.number_input("Days Since Last Training", 0, 365, 30, key="monitor_days")
    with col_m2:
        current_f1 = st.slider("Current Validation F1 Score", 0.0, 1.0, 0.90, 0.01, key="monitor_f1")
    with col_m3:
        drift_detected = st.checkbox("Data Drift Detected?", value=False, key="monitor_drift")
    
    if st.button("📊 Check Model Health", key="monitor_check"):
        recommendation = ""
        color = ""
        
        if current_f1 >= 0.90 and days_since_train < 30 and not drift_detected:
            recommendation = "🟢 **Model is Healthy!** No immediate action needed."
            color = "green"
        elif current_f1 >= 0.85 or (days_since_train >= 30 and days_since_train < 90):
            recommendation = "🟡 **Consider Retraining Soon.** Performance is acceptable but monitor closely."
            color = "orange"
        elif current_f1 < 0.85 or days_since_train >= 90 or drift_detected:
            recommendation = "🔴 **Retrain Immediately Recommended!** Model may be degrading."
            color = "red"
        
        if color == "green":
            st.success(recommendation)
        elif color == "orange":
            st.warning(recommendation)
        else:
            st.error(recommendation)
        
        with st.expander("📋 Detailed Recommendations", expanded=True):
            st.markdown(f"""
            **Your Model Status:**
            - Age: {days_since_train} days
            - Performance (F1): {current_f1:.2f}
            - Drift: {'Yes ⚠️' if drift_detected else 'No ✅'}
            
            **Next Steps:**
            """)
            if color == "red":
                st.markdown("""
                1. **Go to Tab 4** and add recent misclassified cases
                2. **Click "Retrain Now"** to update the model
                3. **Test in Tab 3** to verify improvement
                4. **Re-deploy** using Tab 5
                """)
            elif color == "orange":
                st.markdown("""
                1. Monitor the next 50 predictions closely
                2. If accuracy drops below 85%, retrain
                3. Consider collecting more edge case data in Tab 4
                """)
            else:
                st.markdown("""
                1. Continue normal operations
                2. Review performance weekly
                3. Set up automated monitoring (see guides below)
                """)
    
    st.markdown("---")
    
    st.subheader("6.2 📚 Platform-Specific Monitoring Guides")
    
    platform_tab_docker, platform_tab_azure, platform_tab_aws, platform_tab_gcp = st.tabs([
        "Docker/Local", "Azure ML", "AWS SageMaker", "GCP Vertex AI"
    ])
    
    with platform_tab_docker:
        st.markdown("""
        ### Monitoring Docker/Local Deployments
        
        **1. View Logs:**
        ```bash
        docker logs fraud-api -f
        ```
        
        **2. Monitor Resource Usage:**
        ```bash
        docker stats fraud-api
        ```
        
        **3. Set Up Prometheus + Grafana:**
        - Add metrics endpoint to FastAPI app
        - Configure Prometheus to scrape `/metrics`
        - Create Grafana dashboards for:
          - Request rate (requests/sec)
          - Latency (p50, p95, p99)
          - Prediction distribution
          - Error rate
        
        **4. Health Checks:**
        ```bash
        curl http://localhost:8000/health
        ```
        
        **When to Retrain:**
        - Average fraud probability drifting from baseline
        - Manual review shows >10% false positives
        - New fraud patterns emerge
        """)
    
    with platform_tab_azure:
        st.markdown("""
        ### Monitoring Azure ML
        
        **1. View Metrics in Portal:**
        - Go to Azure ML Studio → Endpoints → Your Model
        - Check "Monitoring" tab for:
          - Request latency
          - CPU/Memory usage
          - Failed requests
        
        **2. Enable Application Insights:**
        ```python
        from azureml.core import Workspace
        from azureml.core.webservice import AciWebservice
        
        # Enable logging
        aci_config = AciWebservice.deploy_configuration(
            enable_app_insights=True
        )
        ```
        
        **3. Data Drift Detection:**
        ```python
        from azureml.datadrift import DataDriftDetector
        
        monitor = DataDriftDetector.create_from_datasets(
            workspace=ws,
            name='fraud-drift-monitor',
            baseline_dataset=train_data,
            target_dataset=live_data
        )
        ```
        
        **4. Alerts:**
        - Set up Azure Alerts for:
          - Latency > 500ms
          - Error rate > 1%
          - Drift score > 0.3
        """)
    
    with platform_tab_aws:
        st.markdown("""
        ### Monitoring AWS SageMaker
        
        **1. CloudWatch Metrics:**
        - ModelLatency
        - ModelInvocations
        - ModelInvocation4XXErrors
        - ModelInvocation5XXErrors
        
        **2. Model Monitor Setup:**
        ```python
        from sagemaker.model_monitor import DataCaptureConfig, DefaultModelMonitor
        
        # Enable data capture
        data_capture_config = DataCaptureConfig(
            enable_capture=True,
            sampling_percentage=100,
            destination_s3_uri='s3://your-bucket/monitoring'
        )
        
        # Create monitor
        my_monitor = DefaultModelMonitor(
            role=role,
            instance_count=1,
            instance_type='ml.m5.xlarge'
        )
        
        my_monitor.suggest_baseline(
            baseline_dataset='s3://your-bucket/baseline.csv',
            dataset_format=DatasetFormat.csv()
        )
        ```
        
        **3. CloudWatch Alarms:**
        ```bash
        aws cloudwatch put-metric-alarm \\
          --alarm-name high-latency \\
          --metric-name ModelLatency \\
          --threshold 500 \\
          --comparison-operator GreaterThanThreshold
        ```
        """)
    
    with platform_tab_gcp:
        st.markdown("""
        ### Monitoring GCP Vertex AI
        
        **1. Cloud Monitoring Dashboard:**
        - Go to Vertex AI → Models → Monitoring
        - View metrics:
          - Prediction count
          - Prediction latency
          - Resource utilization
        
        **2. Model Monitoring Job:**
        ```python
        from google.cloud import aiplatform
        
        # Create monitoring job
        monitoring_job = aiplatform.ModelDeploymentMonitoringJob.create(
            display_name='fraud-monitor',
            endpoint=endpoint,
            logging_sampling_strategy=aiplatform.gapic.SamplingStrategy(
                random_sample_config=aiplatform.gapic.RandomSampleConfig(
                    sample_rate=0.1
                )
            )
        )
        ```
        
        **3. Alerts via Cloud Monitoring:**
        - Set notification channels (email, Slack, PagerDuty)
        - Create alert policies for:
          - High latency
          - Error spikes
          - Prediction drift
        
        **4. Logging:**
        ```bash
        gcloud logging read "resource.type=aiplatform.googleapis.com/Endpoint"
        ```
        """)
    
    st.markdown("---")
    
    st.subheader("6.3 📥 Download Complete Monitoring Guide")
    
    monitoring_guide = """# ML Model Monitoring Guide

## Overview
This guide covers best practices for monitoring machine learning models in production.

## Key Metrics to Track

### 1. Model Performance
- **Accuracy/F1 Score**: Track on validation/test set over time
- **Precision/Recall**: Monitor balance between false positives and false negatives
- **ROC-AUC**: Overall discriminative power

### 2. Operational Metrics
- **Latency**: Response time (p50, p95, p99)
- **Throughput**: Requests per second
- **Error Rate**: Failed predictions / Total predictions
- **Resource Usage**: CPU, Memory, GPU utilization

### 3. Data Quality
- **Data Drift**: Distribution changes in input features
- **Prediction Drift**: Changes in output distribution
- **Missing Values**: % of null/NaN in production data
- **Out-of-Range Values**: Features outside training bounds

## When to Retrain

### Immediate Retraining Triggers:
- Accuracy drops below acceptable threshold (e.g., F1 < 0.85)
- Significant data drift detected (drift score > 0.3)
- New fraud patterns emerge (manual review confirms)
- Major business/regulatory changes

### Scheduled Retraining:
- Monthly for high-change domains (fraud, recommendations)
- Quarterly for stable domains
- After collecting 10,000+ new labeled examples

## Monitoring Dashboard Template

```python
import streamlit as st
import pandas as pd
import plotly.express as px

# Load prediction logs
df = pd.read_csv('prediction_logs.csv')

# Daily prediction volume
st.metric("Today's Predictions", len(df[df['date'] == pd.Timestamp.now().date()]))

# Average fraud rate
avg_fraud = df['prediction'].mean()
st.metric("Fraud Rate", f"{avg_fraud:.1%}")

# Latency distribution
fig = px.histogram(df, x='latency_ms', title='Prediction Latency')
st.plotly_chart(fig)
```

## Best Practices

1. **Automated Alerts**: Set up notifications for anomalies
2. **Regular Audits**: Manual review of high-confidence predictions
3. **A/B Testing**: Compare new models against production baseline
4. **Rollback Plan**: Keep previous model version ready
5. **Documentation**: Log all retrain events and model changes

## Checklist Before Production

- [ ] Monitoring dashboards configured
- [ ] Alerts set up for critical metrics
- [ ] Data capture enabled
- [ ] Retrain schedule defined
- [ ] Rollback procedure tested
- [ ] Performance baseline documented
- [ ] Team trained on monitoring tools

---

**Remember**: A model is only as good as its monitoring. Invest time in observability!
"""
    
    st.download_button(
        label="📥 Download Complete Guide (Markdown)",
        data=monitoring_guide,
        file_name="model_monitoring_guide.md",
        mime="text/markdown",
        key="download_monitor_guide"
    )
    
    st.caption("💡 Tip: Integrate this guide into your team's onboarding documentation!")

