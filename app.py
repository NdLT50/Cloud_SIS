import streamlit as st
import os
import json
import csv
from datetime import datetime
from dotenv import load_dotenv

# Load env variables
load_dotenv()

from src.core.schemas import ProvisioningResult
from src.core.llm_client import analyze_provisioning_request
from src.security.validator import HybridValidator

# Local audit log path
AUDIT_LOG_FILE = "audit_log.csv"

def log_to_csv(request_text, result, total_cost):
    file_exists = os.path.isfile(AUDIT_LOG_FILE)
    try:
        with open(AUDIT_LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Timestamp", "Risk Level", "Action Taken", "Total Cost USD", "Confidence Score", "Request Snippet"])
            writer.writerow([
                datetime.now().isoformat(),
                result.risk_level,
                result.action_taken,
                f"{total_cost:.6f}",
                result.confidence_score,
                request_text[:100].replace('\n', ' ')
            ])
    except Exception as e:
        print(f"Failed to write to audit log: {e}")

st.set_page_config(page_title="AI Infra Provisioning Guard", page_icon="🛡️", layout="wide")

# Initialize Session State
if 'total_requests' not in st.session_state:
    st.session_state.total_requests = 0
if 'total_blocked' not in st.session_state:
    st.session_state.total_blocked = 0
if 'total_downgraded' not in st.session_state:
    st.session_state.total_downgraded = 0
if 'cumulative_cost' not in st.session_state:
    st.session_state.cumulative_cost = 0.0

st.title("🛡️ AI Infra Provisioning Guard")
st.markdown("Strict Security Admin for Triage and Provisioning (Almaty SME Standard)")

# --- Sidebar ---
st.sidebar.header("System Health")
st.sidebar.success("🟢 Status: Active")
st.sidebar.info("🧠 Model: Gemini 1.5 Flash")

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input("Gemini API Key", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
if api_key:
    os.environ["GEMINI_API_KEY"] = api_key

st.sidebar.markdown("---")
st.sidebar.header("FinOps Metrics")
cost_placeholder = st.sidebar.empty()
cost_placeholder.metric(label="Cumulative Session Cost", value=f"${st.session_state.cumulative_cost:.6f}")
    
# --- Risk Dashboard ---
st.markdown("### Risk Dashboard")
dash_cols = st.columns(3)
req_metric = dash_cols[0].empty()
req_metric.metric(label="Total Requests Analysed", value=st.session_state.total_requests)
blk_metric = dash_cols[1].empty()
blk_metric.metric(label="Total BLOCKED Violations", value=st.session_state.total_blocked, delta="- Security Protected", delta_color="inverse")
dng_metric = dash_cols[2].empty()
dng_metric.metric(label="Total Downgraded/Restricted", value=st.session_state.total_downgraded)

st.markdown("---")

st.markdown("### Request Infrastructure Access")
user_request = st.text_area(
    "Request Description", 
    placeholder="Scenario Examples:\n1. 'Create a new read-only user for the accounting department on the production Postgres DB.'\n2. 'Open port 443 for our new web server at 192.168.1.10.'", 
    height=150,
    label_visibility="collapsed"
)

if st.button("Submit Request for Security Triage", type="primary"):
    if not api_key:
        st.error("Please provide a Gemini API Key in the sidebar.")
    elif not user_request.strip():
        st.warning("Please enter a provisioning request.")
    else:
        with st.spinner("Analyzing request and enforcing Least Privilege..."):
            try:
                # 1. LLM Analysis with FinOps
                llm_result, finops_data = analyze_provisioning_request(user_request, ProvisioningResult)
                
                # Update Costs
                current_cost = finops_data['total_cost_usd']
                st.session_state.cumulative_cost += current_cost
                cost_placeholder.metric(label="Cumulative Session Cost", value=f"${st.session_state.cumulative_cost:.6f}", delta=f"+${current_cost:.6f} this txn", delta_color="inverse")
                
                # 2. Hybrid Validation
                validator = HybridValidator()
                final_result = validator.validate(llm_result)
                
                # 3. Observability Logging
                log_to_csv(user_request, final_result, current_cost)
                
                # Update Session Metrics
                st.session_state.total_requests += 1
                if final_result.action_taken == "BLOCKED":
                    st.session_state.total_blocked += 1
                elif final_result.action_taken == "Downgraded":
                    st.session_state.total_downgraded += 1
                    
                # Update dashboard placeholders instantly
                req_metric.metric(label="Total Requests Analysed", value=st.session_state.total_requests)
                blk_metric.metric(label="Total BLOCKED Violations", value=st.session_state.total_blocked, delta="- Security Protected", delta_color="inverse")
                dng_metric.metric(label="Total Downgraded/Restricted", value=st.session_state.total_downgraded)
                
                # --- RESULTS DISPLAY ---
                st.markdown("---")
                
                # Hallucination Guard
                if final_result.confidence_score < 85:
                    st.warning(f"⚠️ **AI Uncertainty Detected (Confidence: {final_result.confidence_score}%): Manual Verification Required**")
                
                if final_result.action_taken == "BLOCKED" or final_result.risk_level >= 8:
                    st.error(f"🚨 ACTION REQUIRED: HIGHEST SECURITY RISK (Level {final_result.risk_level}/10)")
                
                st.subheader("Security Assessment Result")
                
                # Dynamic Coloring based on Risk Level
                if final_result.risk_level >= 8 or final_result.action_taken == "BLOCKED":
                    color = "#ff4b4b" # Red
                elif final_result.risk_level >= 4:
                    color = "#ffa421" # Orange
                else:
                    color = "#00c04b" # Green
                    
                st.markdown(f"**Risk Level:** <span style='color:{color}; font-size: 20px; font-weight: bold;'>{final_result.risk_level}/10</span>", unsafe_allow_html=True)
                st.markdown(f"**Action Taken:** <span style='color:{color}; font-size: 20px; font-weight: bold;'>{final_result.action_taken}</span>", unsafe_allow_html=True)
                
                st.markdown("### Suggested Configuration Fulfillment")
                lang = "sql" if "GRANT" in final_result.suggested_config.upper() else "bash"
                if final_result.action_taken == "BLOCKED":
                    lang = "text"
                st.code(final_result.suggested_config, language=lang)
                
                cols = st.columns(2)
                with cols[0]:
                    st.markdown("### Requested Context")
                    st.write(final_result.requested_permissions)
                with cols[1]:
                    st.markdown("### Approved Context")
                    st.write(final_result.approved_permissions)
                
                st.markdown("### Guard's Reasoning")
                if final_result.action_taken == "BLOCKED":
                    st.error(final_result.reasoning)
                else:
                    st.info(final_result.reasoning)
                
                # Report Download
                report_dict = final_result.model_dump()
                report_dict['timestamp'] = datetime.now().isoformat()
                report_dict['original_request'] = user_request
                report_dict['finops'] = finops_data
                report_json = json.dumps(report_dict, indent=2)
                
                st.download_button(
                    label="📥 Download Security Report (JSON)",
                    data=report_json,
                    file_name="security_triage_report.json",
                    mime="application/json"
                )
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

st.markdown("---")
st.caption("Powered by Gemini 1.5 Flash & Pydantic - Observability Logging Enabled")
