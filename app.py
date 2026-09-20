"""
ContractLens — AI Contract Intelligence & Obligation Tracking Agent
Enterprise B2B SaaS Streamlit Application
"""
import os
import uuid
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import database layer
from db import (
    init_db, save_contract, save_extracted_fields, save_obligations,
    update_obligation_status, save_risks, save_timeline_events,
    save_chat_message, get_chat_history, get_all_contracts, get_contract,
    get_contract_obligations, get_all_obligations, get_contract_risks,
    get_contract_timeline, get_contract_fields, delete_contract
)

# Import agents
from agents import (
    ingest_pdf, search_contract_chunks, extract_contract_intelligence,
    detect_contract_risks, extract_timeline_events, build_timeline_chart,
    compare_contract_versions, answer_contract_question
)

# Page configuration
st.set_page_config(
    page_title="ContractLens | AI Contract Intelligence",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database tables on start
init_db()

# Custom CSS styling for modern enterprise B2B SaaS aesthetics
st.markdown("""
<style>
    /* Google Font: Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Main Background & Text */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 100%);
        border-right: 1px solid #1e293b;
    }
    
    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label {
        color: #f1f5f9 !important;
    }
    
    /* App Top Navigation Banner */
    .brand-container {
        padding: 1rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .brand-logo-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .brand-icon {
        background: #4f46e5;
        width: 40px;
        height: 40px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.3rem;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.35);
    }
    
    .brand-text {
        font-size: 1.35rem;
        font-weight: 700;
        color: #ffffff;
        letter-spacing: -0.02em;
    }
    
    .brand-subtitle {
        font-size: 0.75rem;
        color: #94a3b8;
        font-weight: 500;
        margin-top: 0.1rem;
    }
    
    .disclaimer-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 0.3rem 0.65rem;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        margin-top: 0.8rem;
    }
    
    /* Header Section */
    .page-header {
        background: #ffffff;
        padding: 1.4rem 1.8rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .page-title {
        font-size: 1.6rem;
        font-weight: 700;
        color: #0f172a;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .page-subtitle {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.2rem;
    }

    /* Agent Pipeline Visualizer */
    .agent-pipeline-banner {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.8rem 1.2rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.04);
        overflow-x: auto;
    }

    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.82rem;
        font-weight: 600;
        color: #475569;
    }

    .pipeline-step.active {
        color: #4f46e5;
    }

    .pipeline-step-number {
        width: 22px;
        height: 22px;
        border-radius: 50%;
        background: #e2e8f0;
        color: #475569;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.75rem;
        font-weight: 700;
    }

    .pipeline-step.active .pipeline-step-number {
        background: #4f46e5;
        color: #ffffff;
    }

    .pipeline-arrow {
        color: #cbd5e1;
        font-size: 0.85rem;
    }
    
    /* SaaS Metric Cards */
    .saas-metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.3rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    
    .saas-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px 0 rgba(0, 0, 0, 0.08);
    }
    
    .saas-metric-value {
        font-size: 2.1rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.2;
    }
    
    .saas-metric-label {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748b;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    
    /* White Content Cards */
    .saas-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    }
    
    .saas-card-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.8rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Severity Badges */
    .badge-critical {
        background: #fef2f2;
        color: #991b1b;
        border: 1px solid #fecaca;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .badge-high {
        background: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    
    .badge-warning {
        background: #fffbe6;
        color: #b45309;
        border: 1px solid #fde68a;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }
    
    .badge-success {
        background: #f0fdf4;
        color: #15803d;
        border: 1px solid #bbf7d0;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    .badge-info {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 0.25rem 0.65rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 700;
    }

    /* Citation Tags & Excerpts */
    .citation-chip {
        background: #f1f5f9;
        color: #334155;
        border: 1px solid #cbd5e1;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }

    .source-quote-box {
        background: #f8fafc;
        border-left: 3px solid #4f46e5;
        padding: 0.8rem 1rem;
        margin-top: 0.6rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.88rem;
        color: #334155;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }

    /* Prompt Chips */
    .prompt-chip {
        display: inline-block;
        background: #ffffff;
        color: #4f46e5;
        border: 1px solid #c7d2fe;
        padding: 0.4rem 0.85rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.15s ease;
        margin-right: 0.4rem;
        margin-bottom: 0.4rem;
    }

    .prompt-chip:hover {
        background: #4f46e5;
        color: #ffffff;
        border-color: #4f46e5;
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar():
    """Renders enterprise sidebar navigation & active contract selector."""
    with st.sidebar:
        st.markdown("""
        <div class="brand-container">
            <div class="brand-logo-title">
                <div class="brand-icon">⚖️</div>
                <div>
                    <div class="brand-text">ContractLens</div>
                    <div class="brand-subtitle">AI Contract Intelligence Agent</div>
                </div>
            </div>
            <div class="disclaimer-badge">« AI assistant, not legal advice »</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em;'>Navigation</p>", unsafe_allow_html=True)
        
        menu = st.radio(
            "Navigation Menu",
            [
                "📊 Dashboard",
                "📁 Contracts",
                "📤 Upload Contract",
                "🔍 Contract Analysis",
                "📋 Obligations",
                "⚠️ Risk Center",
                "📅 Timeline & Alerts",
                "⚖️ Compare Versions",
                "💬 Ask Contracts"
            ],
            label_visibility="collapsed"
        )

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em;'>Active Context</p>", unsafe_allow_html=True)

        contracts = get_all_contracts()
        active_contract = None
        
        if contracts:
            contract_options = {f"{c['filename']} ({c['upload_date'][:10]})": c['id'] for c in contracts}
            selected_label = st.selectbox("Select Active Contract", list(contract_options.keys()), label_visibility="collapsed")
            active_contract_id = contract_options[selected_label]
            active_contract = get_contract(active_contract_id)
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.08); padding: 0.8rem; border-radius: 8px; border: 1px solid rgba(255,255,255,0.12); margin-top: 0.5rem;">
                <div style="font-size: 0.8rem; font-weight: 700; color: #ffffff; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{active_contract['filename']}</div>
                <div style="font-size: 0.75rem; color: #cbd5e1; margin-top: 0.2rem;">Risks: <span style="color: #fca5a5; font-weight: 700;">{active_contract.get('risk_count', 0)}</span> | Obligations: <span style="color: #93c5fd; font-weight: 700;">{active_contract.get('obligation_count', 0)}</span></div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No contracts uploaded yet.")

        return menu, contracts, active_contract


def render_agent_pipeline():
    """Displays the Agentic AI visual pipeline banner."""
    st.markdown("""
    <div class="agent-pipeline-banner">
        <div class="pipeline-step active">
            <div class="pipeline-step-number">1</div>
            <span>PDF Ingestion</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step active">
            <div class="pipeline-step-number">2</div>
            <span>Structured Metadata</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step active">
            <div class="pipeline-step-number">3</div>
            <span>Risk Center</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step active">
            <div class="pipeline-step-number">4</div>
            <span>Milestones & Alerts</span>
        </div>
        <div class="pipeline-arrow">➔</div>
        <div class="pipeline-step active">
            <div class="pipeline-step-number">5</div>
            <span>Grounded RAG Q&A</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


def check_api_key():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        try:
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass

    if not api_key:
        st.warning("⚠️ **GEMINI_API_KEY** is not configured. Add your API key to `.env` or Streamlit secrets for full AI capability.")


def main():
    menu, contracts, active_contract = render_sidebar()
    check_api_key()

    # Routing based on selected menu
    if menu == "📊 Dashboard":
        view_dashboard(contracts)
    elif menu == "📁 Contracts":
        view_contracts_library(contracts)
    elif menu == "📤 Upload Contract":
        view_upload()
    elif menu == "🔍 Contract Analysis":
        view_analysis(active_contract)
    elif menu == "📋 Obligations":
        view_obligations(active_contract)
    elif menu == "⚠️ Risk Center":
        view_risk_center(active_contract)
    elif menu == "📅 Timeline & Alerts":
        view_timeline(active_contract)
    elif menu == "⚖️ Compare Versions":
        view_version_compare()
    elif menu == "💬 Ask Contracts":
        view_chat(active_contract)


# -----------------------------------------------------------------------------
# VIEW 1: DASHBOARD
# -----------------------------------------------------------------------------
def view_dashboard(contracts):
    current_date = datetime.now().strftime("%A, %b %d, %Y")
    
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(f"""
        <div style="margin-bottom: 1rem;">
            <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Portfolio Dashboard</h1>
            <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Overview of contract portfolio health, pending obligations, and critical alerts • {current_date}</p>
        </div>
        """, unsafe_allow_html=True)
    with col_h2:
        st.markdown("<div style='text-align: right; padding-top: 0.4rem;'>", unsafe_allow_html=True)
        if st.button("➕ Upload New Contract", type="primary"):
            st.session_state["nav_target"] = "📤 Upload Contract"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    render_agent_pipeline()

    all_obs = get_all_obligations()
    pending_obs = [o for o in all_obs if o.get('status') != 'Completed']
    total_risks = sum(c.get('risk_count', 0) for c in contracts)
    
    # Calculate overdue / due soon timeline events
    total_alerts = 0
    for c in contracts:
        events = get_contract_timeline(c['id'])
        total_alerts += len([e for e in events if e.get('alert_level') in ['Overdue', 'Due within 30 days']])

    # 4 Dynamic Metric Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="saas-metric-card">
            <div class="saas-metric-value" style="color: #4f46e5;">{len(contracts)}</div>
            <div class="saas-metric-label">Contracts Managed</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="saas-metric-card">
            <div class="saas-metric-value" style="color: #d97706;">{len(pending_obs)}</div>
            <div class="saas-metric-label">Active Obligations</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="saas-metric-card">
            <div class="saas-metric-value" style="color: #dc2626;">{total_risks}</div>
            <div class="saas-metric-label">Open Risk Flags</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="saas-metric-card">
            <div class="saas-metric-value" style="color: #2563eb;">{total_alerts}</div>
            <div class="saas-metric-label">30-Day Alerts</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not contracts:
        st.info("👋 **Welcome to ContractLens!** No contracts have been ingested yet. Click on **Upload New Contract** to start automated extraction and risk detection.")
        return

    # Two Main Sections below Metrics
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown("""
        <div class="saas-card">
            <div class="saas-card-header">
                <span>🚨 Alerts Requiring Attention</span>
                <span class="badge-critical">High Priority</span>
            </div>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">Actionable risk flags and critical contract milestones across portfolio.</p>
        """, unsafe_allow_html=True)

        alerts_found = 0
        for c in contracts:
            c_risks = get_contract_risks(c['id'])
            high_risks = [r for r in c_risks if r['severity'] in ['High', 'Critical']]
            for r in high_risks[:3]:
                alerts_found += 1
                st.markdown(f"""
                <div style="background: #fef2f2; border: 1px solid #fecaca; padding: 0.85rem; border-radius: 8px; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="badge-critical">{r['severity']} Risk</span>
                        <span class="citation-chip">Page {r['source_page']}</span>
                    </div>
                    <div style="font-size: 0.9rem; font-weight: 700; color: #991b1b; margin-top: 0.4rem;">{r['risk_title']}</div>
                    <div style="font-size: 0.82rem; color: #7f1d1d; margin-top: 0.2rem;">Contract: <strong>{c['filename']}</strong></div>
                    <div style="font-size: 0.8rem; color: #475569; margin-top: 0.3rem;"><em>"{r['clause_text'][:140]}..."</em></div>
                </div>
                """, unsafe_allow_html=True)

        if alerts_found == 0:
            st.success("✅ No critical risk flags requiring immediate attention.")

        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("""
        <div class="saas-card">
            <div class="saas-card-header">
                <span>📅 Upcoming Obligation Deadlines</span>
                <span class="badge-warning">Action Items</span>
            </div>
            <p style="font-size: 0.85rem; color: #64748b; margin-bottom: 1rem;">Key operational deadlines and party responsibilities.</p>
        """, unsafe_allow_html=True)

        if pending_obs:
            for ob in pending_obs[:4]:
                st.markdown(f"""
                <div style="background: #ffffff; border: 1px solid #e2e8f0; padding: 0.85rem; border-radius: 8px; margin-bottom: 0.75rem; box-shadow: 0 1px 2px rgba(0,0,0,0.03);">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span class="badge-warning">{ob['status']}</span>
                        <span class="citation-chip">Page {ob['source_page']}</span>
                    </div>
                    <div style="font-size: 0.9rem; font-weight: 700; color: #0f172a; margin-top: 0.4rem;">{ob['party_responsible']} — {ob['obligation_text']}</div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.2rem;">Contract: <strong>{ob['filename']}</strong> | Deadline: <strong style="color: #b45309;">{ob['deadline']}</strong></div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No pending obligations found.")

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 2: CONTRACTS LIBRARY
# -----------------------------------------------------------------------------
def view_contracts_library(contracts):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Contracts Library</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Repository of ingested contracts, risk evaluations, and metadata records.</p>
    </div>
    """, unsafe_allow_html=True)

    if not contracts:
        st.info("No contracts found in library. Upload contracts to populate this section.")
        return

    # Search & Filter Controls
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])
    with col_s1:
        search_kw = st.text_input("🔍 Search Contracts", placeholder="Filter by contract name or party...", label_visibility="collapsed")
    with col_s2:
        risk_filter = st.selectbox("Filter Risk", ["All Risk Levels", "High Risk", "Moderate Flags", "Good Standing"], label_visibility="collapsed")
    with col_s3:
        sort_order = st.selectbox("Sort By", ["Newest First", "Oldest First"], label_visibility="collapsed")

    filtered_contracts = list(contracts)
    if search_kw:
        filtered_contracts = [c for c in filtered_contracts if search_kw.lower() in c['filename'].lower()]

    if sort_order == "Oldest First":
        filtered_contracts.reverse()

    st.markdown("<br>", unsafe_allow_html=True)

    for c in filtered_contracts:
        c_id = c['id']
        risks = get_contract_risks(c_id)
        high_risks = [r for r in risks if r['severity'] == 'High']
        
        health_badge = '<span class="badge-success">Good Standing</span>'
        if len(high_risks) > 0:
            health_badge = '<span class="badge-critical">High Risk</span>'
        elif len(risks) > 0:
            health_badge = '<span class="badge-warning">Moderate Flags</span>'

        if risk_filter != "All Risk Levels":
            if risk_filter == "High Risk" and len(high_risks) == 0:
                continue
            elif risk_filter == "Good Standing" and (len(risks) > 0):
                continue
            elif risk_filter == "Moderate Flags" and (len(high_risks) > 0 or len(risks) == 0):
                continue

        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div>
                    <div style="display: flex; align-items: center; gap: 0.6rem;">
                        <h3 style="margin:0; font-size: 1.15rem; font-weight: 700; color: #0f172a;">📄 {c['filename']}</h3>
                        {health_badge}
                    </div>
                    <div style="font-size: 0.82rem; color: #64748b; margin-top: 0.4rem;">
                        Uploaded: <strong>{c['upload_date']}</strong> | Status: <strong>{c['status']}</strong>
                    </div>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-top: 1rem; background: #f8fafc; padding: 0.85rem; border-radius: 8px; border: 1px solid #f1f5f9;">
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">EFFECTIVE DATE</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a;">{c['effective_date']}</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">EXPIRATION DATE</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #0f172a;">{c['expiration_date']}</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">OBLIGATIONS</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #2563eb;">{c.get('obligation_count', 0)} tracked</div>
                </div>
                <div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">RISK FLAGS</div>
                    <div style="font-size: 0.88rem; font-weight: 700; color: #dc2626;">{c.get('risk_count', 0)} items</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_b1, col_b2 = st.columns([4, 1])
        with col_b2:
            if st.button("🗑️ Delete Contract", key=f"del_lib_{c['id']}"):
                delete_contract(c['id'])
                st.rerun()


# -----------------------------------------------------------------------------
# VIEW 3: UPLOAD CONTRACT
# -----------------------------------------------------------------------------
def view_upload():
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Upload a Business Contract</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Upload PDF documents to initiate ingestion, RAG vector indexing, and multi-agent AI extraction.</p>
    </div>
    """, unsafe_allow_html=True)

    render_agent_pipeline()

    st.markdown("""
    <div class="saas-card" style="text-align: center; border: 2px dashed #cbd5e1; padding: 2.5rem;">
        <div style="font-size: 2.5rem; color: #4f46e5; margin-bottom: 0.5rem;">📄</div>
        <h3 style="margin: 0; color: #0f172a; font-size: 1.25rem;">Select or Drag PDF Contracts</h3>
        <p style="color: #64748b; font-size: 0.88rem; margin-top: 0.3rem;">Supports enterprise SaaS agreements, vendor contracts, SLAs, and amendments.</p>
    </div>
    """, unsafe_allow_html=True)

    uploaded_files = st.file_uploader("Choose PDF Contract Files", type=["pdf"], accept_multiple_files=True, label_visibility="collapsed")

    if uploaded_files:
        st.markdown(f"### Selected Files ({len(uploaded_files)})")
        for f in uploaded_files:
            st.markdown(f"▪️ **{f.name}** ({f.size / 1024:.1f} KB)")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Analyze Contracts with AI", type="primary"):
            for uploaded_file in uploaded_files:
                filename = uploaded_file.name
                contract_id = f"cnt_{uuid.uuid4().hex[:8]}"

                try:
                    with st.spinner(f"Ingesting & Executing Multi-Agent Analysis on {filename}..."):
                        pdf_bytes = uploaded_file.read()
                        
                        # Agent 1: Ingestion
                        pages_text, chunk_count = ingest_pdf(pdf_bytes, filename, contract_id)

                        # Agent 2: Extraction
                        extraction, obligations = extract_contract_intelligence(pages_text, filename)

                        # Agent 3: Risk Detection
                        risks = detect_contract_risks(pages_text, filename)

                        # Agent 4: Timeline Extraction
                        timeline_events = extract_timeline_events(pages_text, filename, extraction)

                        # Save to SQLite Database
                        save_contract(
                            contract_id=contract_id,
                            filename=filename,
                            status="Analyzed",
                            effective_date=extraction.effective_date.value,
                            expiration_date=extraction.expiration_date.value,
                            obligation_count=len(obligations),
                            risk_count=len(risks),
                            summary_json=json.dumps(extraction.model_dump())
                        )

                        save_extracted_fields(contract_id, [
                            {"field_name": "Effective Date", "value": extraction.effective_date.value, "source_page": extraction.effective_date.source_page, "source_clause": extraction.effective_date.source_clause},
                            {"field_name": "Expiration Date", "value": extraction.expiration_date.value, "source_page": extraction.expiration_date.source_page, "source_clause": extraction.expiration_date.source_clause},
                            {"field_name": "Renewal Terms", "value": extraction.renewal_terms.value, "source_page": extraction.renewal_terms.source_page, "source_clause": extraction.renewal_terms.source_clause},
                            {"field_name": "Payment Terms", "value": extraction.payment_terms.value, "source_page": extraction.payment_terms.source_page, "source_clause": extraction.payment_terms.source_clause},
                            {"field_name": "Termination Conditions", "value": extraction.termination_conditions.value, "source_page": extraction.termination_conditions.source_page, "source_clause": extraction.termination_conditions.source_clause},
                            {"field_name": "Governing Law", "value": extraction.governing_law.value, "source_page": extraction.governing_law.source_page, "source_clause": extraction.governing_law.source_clause},
                        ])
                        save_obligations(contract_id, obligations)
                        save_risks(contract_id, risks)
                        save_timeline_events(contract_id, timeline_events)

                    st.success(f"✅ Successfully ingested & analyzed **{filename}** ({len(pages_text)} pages, {chunk_count} RAG chunks, {len(obligations)} obligations, {len(risks)} risk flags).")
                except ValueError as ve:
                    st.warning(str(ve))
                except Exception as e:
                    st.error(f"❌ Analysis Notice for **{filename}**: {str(e)}")
            
            st.balloons()


# -----------------------------------------------------------------------------
# VIEW 4: CONTRACT ANALYSIS
# -----------------------------------------------------------------------------
def view_analysis(active_contract):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Contract Intelligence Analysis</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Deep-dive clause analysis, extracted metadata, and source traceability.</p>
    </div>
    """, unsafe_allow_html=True)

    if not active_contract:
        st.info("Please select an active contract from the sidebar or upload a contract to view detailed analysis.")
        return

    contract_id = active_contract['id']
    st.markdown(f"### 📄 Active Context: {active_contract['filename']}")

    # Executive Summary Card
    summary_data = {}
    try:
        summary_data = json.loads(active_contract['summary_json'])
    except Exception:
        pass

    exec_summary = summary_data.get("executive_summary", "Executive summary unavailable.")
    st.markdown(f"""
    <div class="saas-card" style="background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%); border-left: 4px solid #4f46e5;">
        <h4 style="margin-top:0; color:#4f46e5; font-weight: 700;">Executive Business Summary</h4>
        <p style="font-size: 0.92rem; color: #334155; line-height: 1.6;">{exec_summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # Search Inside Contract
    st.subheader("🔍 Search Contract Content")
    search_query = st.text_input("Search keywords, clauses, parties, or payment terms...", placeholder="e.g. liability, termination, Net 30", label_visibility="collapsed")
    if search_query:
        results = search_contract_chunks(contract_id, search_query, top_k=5)
        st.markdown(f"Found {len(results)} relevant page excerpts:")
        for r in results:
            st.markdown(f"""
            <div class="source-quote-box">
                <span class="citation-chip">Page {r['page_number']}</span>
                <p style="margin-top: 0.4rem; margin-bottom: 0; color: #0f172a;">"{r['text']}"</p>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Key Extracted Fields & Source Traceability")

    fields = get_contract_fields(contract_id)
    if fields:
        for f in fields:
            with st.expander(f"📌 {f['field_name']}: {f['value']}", expanded=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    if f['source_clause']:
                        st.markdown(f"**Source Clause:** *\"{f['source_clause']}\"*")
                    else:
                        st.markdown("*No direct clause snippet quoted.*")
                with col2:
                    st.markdown(f"<span class='citation-chip'>Page {f['source_page']}</span>", unsafe_allow_html=True)
                    st.caption(f"Confidence: {f['confidence']*100:.0f}%")
    else:
        st.write("No extracted fields recorded.")


# -----------------------------------------------------------------------------
# VIEW 5: OBLIGATIONS
# -----------------------------------------------------------------------------
def view_obligations(active_contract):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Obligation Tracking Agent</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Monitor and update operational commitments across contract counterparties.</p>
    </div>
    """, unsafe_allow_html=True)

    if active_contract:
        obligations = get_contract_obligations(active_contract['id'])
        st.caption(f"Viewing obligations for active contract: **{active_contract['filename']}**")
    else:
        obligations = get_all_obligations()
        st.caption("Viewing all obligations across all contracts.")

    if not obligations:
        st.info("No obligations recorded for this contract.")
        return

    # Filter Bar
    status_filter = st.selectbox("Filter by Status", ["All", "Upcoming", "Due Soon", "Overdue", "Completed"])
    if status_filter != "All":
        filtered_obs = [o for o in obligations if o['status'] == status_filter]
    else:
        filtered_obs = obligations

    st.markdown(f"Displaying {len(filtered_obs)} obligations:")

    for ob in filtered_obs:
        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h4 style="margin:0; color:#0f172a;">{ob['party_responsible']} — {ob['obligation_text']}</h4>
                <span class="citation-chip">Page {ob['source_page']}</span>
            </div>
            <p style="margin-top: 0.5rem; color: #475569; font-size: 0.88rem;">
                <strong>Deadline:</strong> <span style="color: #b45309;">{ob['deadline']}</span> ({ob['deadline_type']}) | <strong>Frequency:</strong> {ob['frequency']}<br>
                <strong>Source Clause:</strong> <em>"{ob['clause_text']}"</em>
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns([3, 1])
        with col1:
            st.write(f"Current Status: **{ob['status']}**")
        with col2:
            if ob['status'] != 'Completed':
                if st.button("Mark Completed", key=f"ob_comp_{ob['id']}"):
                    update_obligation_status(ob['id'], 'Completed')
                    st.rerun()
            else:
                if st.button("Re-open Obligation", key=f"ob_open_{ob['id']}"):
                    update_obligation_status(ob['id'], 'Upcoming')
                    st.rerun()


# -----------------------------------------------------------------------------
# VIEW 6: RISK CENTER
# -----------------------------------------------------------------------------
def view_risk_center(active_contract):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Risk Center — Legal & Operational Detector</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Automated detection of uncapped liability, auto-renewals, high penalties, and ambiguous obligations.</p>
    </div>
    """, unsafe_allow_html=True)

    if not active_contract:
        st.info("Please select an active contract from the sidebar.")
        return

    risks = get_contract_risks(active_contract['id'])
    if not risks:
        st.success("🎉 No high risk flags identified for this contract.")
        return

    st.markdown("""
    <div style="background: #fffbe6; border: 1px solid #fde68a; padding: 0.85rem 1.2rem; border-radius: 8px; margin-bottom: 1.2rem;">
        <strong style="color: #b45309;">⚠️ Legal Disclaimer:</strong> <span style="color: #78350f; font-size: 0.88rem;">AI assistant output, not formal legal advice. Human/legal review is recommended for flagged clauses.</span>
    </div>
    """, unsafe_allow_html=True)

    for r in risks:
        badge_class = "badge-warning"
        if r['severity'] in ["High", "Critical"]:
            badge_class = "badge-critical"
        elif r['severity'] == "Low":
            badge_class = "badge-success"

        st.markdown(f"""
        <div class="saas-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin:0; color:#0f172a; font-size: 1.1rem;">{r['risk_title']}</h3>
                <div>
                    <span class="{badge_class}">{r['severity']} Risk</span>
                    <span class="citation-chip" style="margin-left: 0.4rem;">Page {r['source_page']}</span>
                </div>
            </div>
            <p style="margin-top: 0.6rem; color: #334155; font-size: 0.9rem;"><strong>Reason:</strong> {r['reason']}</p>
            <div class="source-quote-box">
                <strong>Verbatim Clause:</strong> <em>"{r['clause_text']}"</em>
            </div>
            <p style="margin-top: 0.6rem; color: #dc2626; font-size: 0.85rem; font-weight: 600;">
                👉 {r['action_recommended']}
            </p>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 7: TIMELINE
# -----------------------------------------------------------------------------
def view_timeline(active_contract):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Timeline & Milestone Agent</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Interactive milestone tracking with 30-day proximity alerts.</p>
    </div>
    """, unsafe_allow_html=True)

    if not active_contract:
        st.info("Please select an active contract from the sidebar.")
        return

    events = get_contract_timeline(active_contract['id'])
    if not events:
        st.info("No timeline events extracted for this contract.")
        return

    # Plotly Timeline Chart
    fig = build_timeline_chart(events)
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("30-Day Proximity Alerts")
    
    overdue = [e for e in events if e['alert_level'] == 'Overdue']
    due_30 = [e for e in events if e['alert_level'] == 'Due within 30 days']
    upcoming = [e for e in events if e['alert_level'] == 'Upcoming']

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"### 🔴 Overdue ({len(overdue)})")
        for e in overdue:
            st.error(f"**{e['event_title']}**\nDate: `{e['date_str']}` (Page {e['source_page']})")
    with col2:
        st.markdown(f"### 🟠 Due in 30 Days ({len(due_30)})")
        for e in due_30:
            st.warning(f"**{e['event_title']}**\nDate: `{e['date_str']}` (Page {e['source_page']})")
    with col3:
        st.markdown(f"### 🟢 Upcoming ({len(upcoming)})")
        for e in upcoming:
            st.success(f"**{e['event_title']}**\nDate: `{e['date_str']}` (Page {e['source_page']})")


# -----------------------------------------------------------------------------
# VIEW 8: VERSION COMPARE
# -----------------------------------------------------------------------------
def view_version_compare():
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Version Comparison Agent</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Upload two contract versions for exact text diffing and Gemini AI business impact evaluation.</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        v1_file = st.file_uploader("Upload Version 1 (V1 PDF)", type=["pdf"], key="v1_pdf")
    with col2:
        v2_file = st.file_uploader("Upload Version 2 (V2 PDF)", type=["pdf"], key="v2_pdf")

    if v1_file and v2_file:
        if st.button("🔍 Run Version Comparison", type="primary"):
            with st.spinner("Analyzing textual differences and evaluating business impact..."):
                v1_bytes = v1_file.read()
                v2_bytes = v2_file.read()
                
                diffs = compare_contract_versions(v1_bytes, v1_file.name, v2_bytes, v2_file.name)

            if not diffs:
                st.success("No significant textual changes detected between V1 and V2.")
                return

            st.subheader(f"Comparison Summary: {len(diffs)} Changes Identified")
            
            for d in diffs:
                st.markdown(f"""
                <div class="saas-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin:0; color:#0f172a;">{d['clause_name']}</h4>
                        <span class="citation-chip">{d['change_type']} (Page {d['source_page']})</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.8rem;">
                        <div style="background: #fef2f2; padding: 0.8rem; border-radius: 6px; border: 1px solid #fecaca;">
                            <strong style="color: #991b1b;">V1 Text:</strong><br>
                            <small style="color: #7f1d1d;">"{d['v1_text']}"</small>
                        </div>
                        <div style="background: #f0fdf4; padding: 0.8rem; border-radius: 6px; border: 1px solid #bbf7d0;">
                            <strong style="color: #15803d;">V2 Text:</strong><br>
                            <small style="color: #14532d;">"{d['v2_text']}"</small>
                        </div>
                    </div>
                    <div style="margin-top: 0.8rem; background: #eff6ff; padding: 0.8rem; border-radius: 6px; border: 1px solid #bfdbfe;">
                        <strong style="color: #1d4ed8;">💡 AI Business Impact Explanation:</strong><br>
                        <span style="color: #1e40af; font-size: 0.88rem;">{d['business_impact']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 9: ASK CONTRACTS (AI CHAT)
# -----------------------------------------------------------------------------
def view_chat(active_contract):
    st.markdown("""
    <div style="margin-bottom: 1rem;">
        <h1 style="font-size: 1.8rem; font-weight: 800; color: #0f172a; margin: 0;">Ask Contracts — Grounded RAG Assistant</h1>
        <p style="font-size: 0.9rem; color: #64748b; margin: 0.2rem 0 0 0;">Ask natural-language business questions grounded strictly in contract chunks with page citations.</p>
    </div>
    """, unsafe_allow_html=True)

    if not active_contract:
        st.info("Please select an active contract from the sidebar to start asking questions.")
        return

    contract_id = active_contract['id']
    st.markdown(f"### 💬 Context: {active_contract['filename']}")

    # Display Chat History
    history = get_chat_history(contract_id)
    for msg in history:
        with st.chat_message(msg['role']):
            st.markdown(msg['message'])
            if msg['citations']:
                with st.expander("🔍 View Source Evidence"):
                    for c in msg['citations']:
                        st.markdown(f"**Page {c['page_number']}**: *\"{c['snippet']}\"*")

    # Suggested Question Chips
    st.markdown("<p style='font-size: 0.82rem; font-weight: 700; color: #64748b; margin-top: 1rem; margin-bottom: 0.4rem;'>Suggested Questions:</p>", unsafe_allow_html=True)
    
    chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
    selected_prompt = None
    with chip_col1:
        if st.button("💳 What are payment terms?", key="chip1"):
            selected_prompt = "What are the payment terms?"
    with chip_col2:
        if st.button("⚠️ What are key risks?", key="chip2"):
            selected_prompt = "What are the key risks in this contract?"
    with chip_col3:
        if st.button("🔄 When is renewal?", key="chip3"):
            selected_prompt = "When does this contract renew and what notice is required?"
    with chip_col4:
        if st.button("📋 Show obligations", key="chip4"):
            selected_prompt = "What are the key obligations for each party?"

    # Chat Input
    user_question = st.chat_input("Ask a business question about this contract...")
    
    prompt_to_run = user_question or selected_prompt

    if prompt_to_run:
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt_to_run)
        save_chat_message(contract_id, "user", prompt_to_run)

        # Generate grounded answer
        with st.chat_message("assistant"):
            with st.spinner("Searching contract chunks & generating grounded answer..."):
                answer, citations = answer_contract_question(contract_id, active_contract['filename'], prompt_to_run)
                st.markdown(answer)
                if citations:
                    with st.expander("🔍 View Source Evidence"):
                        for c in citations:
                            st.markdown(f"**Page {c['page_number']}**: *\"{c['snippet']}\"*")

        save_chat_message(contract_id, "assistant", answer, citations)


if __name__ == "__main__":
    main()
