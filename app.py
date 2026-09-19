"""
ContractLens — AI Contract Intelligence & Obligation Tracking Agent
Main Streamlit Web Application
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

# Custom CSS styling for premium SaaS aesthetics
st.markdown("""
<style>
    /* Main Theme Variables & Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    
    /* Header Container */
    .app-header {
        background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #1e293b 100%);
        padding: 1.8rem 2rem;
        border-radius: 14px;
        border: 1px solid rgba(99, 102, 241, 0.25);
        margin-bottom: 1.8rem;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    
    .app-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        letter-spacing: -0.02em;
    }
    
    .app-subtitle {
        font-size: 1.05rem;
        color: #a5b4fc;
        margin-top: 0.3rem;
        font-weight: 400;
    }
    
    .disclaimer-badge {
        display: inline-block;
        background: rgba(239, 68, 68, 0.15);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 500;
        margin-top: 0.6rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid rgba(148, 163, 184, 0.15);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    
    .metric-card:hover {
        border-color: rgba(99, 102, 241, 0.4);
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: #6366f1;
        margin-bottom: 0.2rem;
    }
    
    .metric-label {
        font-size: 0.88rem;
        color: #94a3b8;
        font-weight: 500;
    }
    
    /* Content Cards */
    .content-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(148, 163, 184, 0.12);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
    }
    
    /* Badges */
    .badge-high {
        background: rgba(239, 68, 68, 0.2);
        color: #fca5a5;
        border: 1px solid rgba(239, 68, 68, 0.4);
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-medium {
        background: rgba(245, 158, 11, 0.2);
        color: #fde68a;
        border: 1px solid rgba(245, 158, 11, 0.4);
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .badge-low {
        background: rgba(16, 185, 129, 0.2);
        color: #6ee7b7;
        border: 1px solid rgba(16, 185, 129, 0.4);
        padding: 0.25rem 0.6rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .citation-tag {
        background: rgba(99, 102, 241, 0.2);
        color: #c7d2fe;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.78rem;
        font-weight: 500;
    }

    /* Citation Box */
    .citation-box {
        background: rgba(15, 23, 42, 0.8);
        border-left: 3px solid #6366f1;
        padding: 0.8rem 1rem;
        margin-top: 0.5rem;
        border-radius: 0 8px 8px 0;
        font-size: 0.88rem;
        color: #cbd5e1;
    }
</style>
""", unsafe_allow_html=True)


def render_header():
    st.markdown("""
    <div class="app-header">
        <div class="app-title">ContractLens</div>
        <div class="app-subtitle">AI Contract Intelligence & Obligation Tracking Agent</div>
        <div class="disclaimer-badge">« AI assistant, not legal advice. »</div>
    </div>
    """, unsafe_allow_html=True)


def check_api_key():
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        st.warning("⚠️ GEMINI_API_KEY is not configured in `.env`. The application will operate with rule-based fallbacks. Add your Gemini API key to `.env` for full AI power.")


def main():
    render_header()
    check_api_key()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio(
        "Select Feature View",
        [
            "📊 Dashboard",
            "📤 Upload Contracts",
            "🔍 Contract Analysis",
            "📋 Obligations",
            "⚠️ Risk Center",
            "📅 Timeline",
            "⚖️ Version Compare",
            "💬 Contract Chat"
        ]
    )

    # Active Contract Selector in Sidebar
    contracts = get_all_contracts()
    active_contract_id = None
    
    if contracts:
        st.sidebar.markdown("---")
        st.sidebar.subheader("Active Contract")
        contract_options = {f"{c['filename']} ({c['upload_date'][:10]})": c['id'] for c in contracts}
        selected_label = st.sidebar.selectbox("Select Contract Context", list(contract_options.keys()))
        active_contract_id = contract_options[selected_label]
        active_contract = get_contract(active_contract_id)
    else:
        active_contract = None

    # Routing based on selected menu
    if menu == "📊 Dashboard":
        view_dashboard(contracts)
    elif menu == "📤 Upload Contracts":
        view_upload()
    elif menu == "🔍 Contract Analysis":
        view_analysis(active_contract)
    elif menu == "📋 Obligations":
        view_obligations(active_contract)
    elif menu == "⚠️ Risk Center":
        view_risk_center(active_contract)
    elif menu == "📅 Timeline":
        view_timeline(active_contract)
    elif menu == "⚖️ Version Compare":
        view_version_compare()
    elif menu == "💬 Contract Chat":
        view_chat(active_contract)


# -----------------------------------------------------------------------------
# VIEW 1: DASHBOARD
# -----------------------------------------------------------------------------
def view_dashboard(contracts):
    st.header("Executive Dashboard")
    
    all_obs = get_all_obligations()
    pending_obs = [o for o in all_obs if o.get('status') != 'Completed']
    
    # Calculate total risks across contracts
    total_risks = sum(c.get('risk_count', 0) for c in contracts)
    
    # Top Metrics Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(contracts)}</div>
            <div class="metric-label">Contracts Managed</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #f59e0b;">{len(pending_obs)}</div>
            <div class="metric-label">Active Obligations</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #ef4444;">{total_risks}</div>
            <div class="metric-label">High-Risk Clauses</div>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value" style="color: #10b981;">{len(contracts)}</div>
            <div class="metric-label">Analyzed Records</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    if not contracts:
        st.info("👋 Welcome to ContractLens! No contracts have been uploaded yet. Click on **Upload Contracts** in the sidebar to get started.")
        return

    st.subheader("Contract Library")
    
    # Contract Health Overview Table
    for c in contracts:
        with st.container():
            c_id = c['id']
            risks = get_contract_risks(c_id)
            high_risks = [r for r in risks if r['severity'] == 'High']
            
            health_color = "#10b981"  # Green
            health_text = "Good Standing"
            if len(high_risks) > 0:
                health_color = "#ef4444"  # Red
                health_text = "Review Recommended"
            elif len(risks) > 2:
                health_color = "#f59e0b"  # Orange
                health_text = "Moderate Flags"

            col_a, col_b, col_c, col_d = st.columns([3, 2, 2, 1])
            with col_a:
                st.markdown(f"**📄 {c['filename']}**")
                st.caption(f"Uploaded: {c['upload_date']}")
            with col_b:
                st.markdown(f"Effective: `{c['effective_date']}`")
                st.markdown(f"Expiration: `{c['expiration_date']}`")
            with col_c:
                st.markdown(f"**Contract Review Overview**")
                st.markdown(f"<span style='color: {health_color}; font-weight: 600;'>● {len(risks)} Human Review Item(s)</span>", unsafe_allow_html=True)
            with col_d:
                if st.button("Delete", key=f"del_{c['id']}"):
                    delete_contract(c['id'])
                    st.rerun()
            st.divider()


# -----------------------------------------------------------------------------
# VIEW 2: UPLOAD CONTRACTS
# -----------------------------------------------------------------------------
def view_upload():
    st.header("Upload Contracts")
    st.markdown("Upload one or multiple PDF contract documents to trigger ingestion, RAG vector indexing, and multi-agent extraction.")

    uploaded_files = st.file_uploader("Choose PDF Contract Files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files:
        if st.button("🚀 Analyze Contracts", type="primary"):
            for uploaded_file in uploaded_files:
                filename = uploaded_file.name
                contract_id = f"cnt_{uuid.uuid4().hex[:8]}"

                try:
                    with st.spinner(f"Ingesting & Analyzing {filename}..."):
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

                        # Save extracted fields
                        fields = [
                            {"field_name": "Effective Date", "value": extraction.effective_date.value, "source_page": extraction.effective_date.source_page, "source_clause": extraction.effective_date.source_clause},
                            {"field_name": "Expiration Date", "value": extraction.expiration_date.value, "source_page": extraction.expiration_date.source_page, "source_clause": extraction.expiration_date.source_clause},
                            {"field_name": "Renewal Terms", "value": extraction.renewal_terms.value, "source_page": extraction.renewal_terms.source_page, "source_clause": extraction.renewal_terms.source_clause},
                            {"field_name": "Payment Terms", "value": extraction.payment_terms.value, "source_page": extraction.payment_terms.source_page, "source_clause": extraction.payment_terms.source_clause},
                            {"field_name": "Termination Conditions", "value": extraction.termination_conditions.value, "source_page": extraction.termination_conditions.source_page, "source_clause": extraction.termination_conditions.source_clause},
                            {"field_name": "Governing Law", "value": extraction.governing_law.value, "source_page": extraction.governing_law.source_page, "source_clause": extraction.governing_law.source_clause},
                        ]
                        save_extracted_fields(contract_id, fields)
                        save_obligations(contract_id, obligations)
                        save_risks(contract_id, risks)
                        save_timeline_events(contract_id, timeline_events)

                    st.success(f"✅ Successfully ingested & analyzed **{filename}** ({len(pages_text)} pages, {chunk_count} RAG chunks, {len(obligations)} obligations, {len(risks)} risk flags).")
                except ValueError as ve:
                    st.warning(str(ve))
                except Exception as e:
                    st.error(f"❌ Gemini AI Analysis Error for **{filename}**: {str(e)}")
            
            st.balloons()


# -----------------------------------------------------------------------------
# VIEW 3: CONTRACT ANALYSIS
# -----------------------------------------------------------------------------
def view_analysis(active_contract):
    st.header("Contract Analysis & Intelligence")
    
    if not active_contract:
        st.info("Please select an active contract from the sidebar or upload a contract to view detailed analysis.")
        return

    contract_id = active_contract['id']
    st.subheader(f"📄 {active_contract['filename']}")

    # Executive Summary Card
    summary_data = {}
    try:
        summary_data = json.loads(active_contract['summary_json'])
    except Exception:
        pass

    exec_summary = summary_data.get("executive_summary", "Executive summary unavailable.")
    st.markdown(f"""
    <div class="content-card">
        <h4 style="margin-top:0; color:#a5b4fc;">Executive Summary</h4>
        <p>{exec_summary}</p>
    </div>
    """, unsafe_allow_html=True)

    # Search Inside Contract
    st.subheader("🔍 Search Contract Content")
    search_query = st.text_input("Search keywords, clauses, parties, or payment terms...", placeholder="e.g. liability, termination, Net 30")
    if search_query:
        results = search_contract_chunks(contract_id, search_query, top_k=5)
        st.markdown(f"Found {len(results)} relevant page excerpts:")
        for r in results:
            st.markdown(f"""
            <div class="citation-box">
                <span class="citation-tag">Page {r['page_number']}</span>
                <p style="margin-top: 0.4rem; margin-bottom: 0;">"{r['text']}"</p>
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
                    st.markdown(f"<span class='citation-tag'>Source: Page {f['source_page']}</span>", unsafe_allow_html=True)
                    st.caption(f"Confidence: {f['confidence']*100:.0f}%")
    else:
        st.write("No extracted fields recorded.")


# -----------------------------------------------------------------------------
# VIEW 4: OBLIGATIONS
# -----------------------------------------------------------------------------
def view_obligations(active_contract):
    st.header("Obligation Tracking Agent")
    st.markdown("Monitor and update operational obligations across contract counterparties.")

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
        with st.container():
            st.markdown(f"""
            <div class="content-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h4 style="margin:0; color:#ffffff;">{ob['party_responsible']} — {ob['obligation_text']}</h4>
                    <span class="citation-tag">Page {ob['source_page']}</span>
                </div>
                <p style="margin-top: 0.5rem; color: #94a3b8;">
                    <strong>Deadline:</strong> {ob['deadline']} ({ob['deadline_type']}) | <strong>Frequency:</strong> {ob['frequency']}<br>
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
                    if st.button("Re-open", key=f"ob_open_{ob['id']}"):
                        update_obligation_status(ob['id'], 'Upcoming')
                        st.rerun()
            st.divider()


# -----------------------------------------------------------------------------
# VIEW 5: RISK CENTER
# -----------------------------------------------------------------------------
def view_risk_center(active_contract):
    st.header("Risk Center — Human Review Detector")
    st.markdown("Automated detection of uncapped liability, auto-renewals, high penalties, and ambiguous obligations.")

    if not active_contract:
        st.info("Please select an active contract from the sidebar.")
        return

    risks = get_contract_risks(active_contract['id'])
    if not risks:
        st.success("🎉 No high risk flags identified for this contract.")
        return

    st.warning("⚠️ **Legal Disclaimer:** Insights below highlight areas of potential operational risk. Human review is recommended.")

    for r in risks:
        badge_class = "badge-medium"
        if r['severity'] == "High":
            badge_class = "badge-high"
        elif r['severity'] == "Low":
            badge_class = "badge-low"

        st.markdown(f"""
        <div class="content-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin:0; color:#ffffff;">{r['risk_title']}</h3>
                <div>
                    <span class="{badge_class}">{r['severity']} Risk</span>
                    <span class="citation-tag" style="margin-left: 0.4rem;">Page {r['source_page']}</span>
                </div>
            </div>
            <p style="margin-top: 0.8rem; color: #cbd5e1;"><strong>Reason:</strong> {r['reason']}</p>
            <div class="citation-box">
                <strong>Verbatim Clause:</strong> <em>"{r['clause_text']}"</em>
            </div>
            <p style="margin-top: 0.8rem; color: #fca5a5; font-weight: 500;">
                👉 {r['action_recommended']}
            </p>
        </div>
        """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 6: TIMELINE
# -----------------------------------------------------------------------------
def view_timeline(active_contract):
    st.header("Timeline & Milestone Agent")
    st.markdown("Interactive date milestone tracking with 30-day proximity alerts.")

    if not active_contract:
        st.info("Please select an active contract from the sidebar.")
        return

    events = get_contract_timeline(active_contract['id'])
    if not events:
        st.info("No timeline events extracted.")
        return

    # Plotly Timeline Chart
    fig = build_timeline_chart(events)
    st.plotly_chart(fig, use_container_width=True)

    # 30-Day Alert Section
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
# VIEW 7: VERSION COMPARE
# -----------------------------------------------------------------------------
def view_version_compare():
    st.header("Version Comparison Agent")
    st.markdown("Upload two versions of a contract to run exact text diffing + AI business impact analysis.")

    col1, col2 = st.columns(2)
    with col1:
        v1_file = st.file_uploader("Upload Version 1 (V1 PDF)", type=["pdf"], key="v1_pdf")
    with col2:
        v2_file = st.file_uploader("Upload Version 2 (V2 PDF)", type=["pdf"], key="v2_pdf")

    if v1_file and v2_file:
        if st.button("🔍 Compare Versions", type="primary"):
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
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between;">
                        <h4 style="margin:0; color:#a5b4fc;">{d['clause_name']}</h4>
                        <span class="citation-tag">{d['change_type']} ({d['source_page']})</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 0.8rem;">
                        <div style="background: rgba(239, 68, 68, 0.1); padding: 0.8rem; border-radius: 6px; border: 1px solid rgba(239, 68, 68, 0.2);">
                            <strong style="color: #fca5a5;">V1 Text:</strong><br>
                            <small>"{d['v1_text']}"</small>
                        </div>
                        <div style="background: rgba(16, 185, 129, 0.1); padding: 0.8rem; border-radius: 6px; border: 1px solid rgba(16, 185, 129, 0.2);">
                            <strong style="color: #6ee7b7;">V2 Text:</strong><br>
                            <small>"{d['v2_text']}"</small>
                        </div>
                    </div>
                    <div style="margin-top: 0.8rem; background: rgba(99, 102, 241, 0.15); padding: 0.8rem; border-radius: 6px;">
                        <strong style="color: #c7d2fe;">💡 AI Business Impact Explanation:</strong><br>
                        <span>{d['business_impact']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# VIEW 8: CONTRACT CHAT
# -----------------------------------------------------------------------------
def view_chat(active_contract):
    st.header("Contract RAG Q&A Chatbot")
    st.markdown("Ask natural language questions. Answers are strictly grounded in retrieved contract chunks with page citations.")

    if not active_contract:
        st.info("Please select an active contract from the sidebar to start chatting.")
        return

    contract_id = active_contract['id']
    st.caption(f"Chatting with context from: **{active_contract['filename']}**")

    # Display Chat History
    history = get_chat_history(contract_id)
    for msg in history:
        with st.chat_message(msg['role']):
            st.markdown(msg['message'])
            if msg['citations']:
                with st.expander("🔍 View Source Evidence"):
                    for c in msg['citations']:
                        st.markdown(f"**Page {c['page_number']}**: *\"{c['snippet']}\"*")

    # Chat Input
    if user_question := st.chat_input("e.g. When does this contract expire? What are the payment terms?"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_question)
        save_chat_message(contract_id, "user", user_question)

        # Generate grounded answer
        with st.chat_message("assistant"):
            with st.spinner("Searching contract chunks..."):
                answer, citations = answer_contract_question(contract_id, active_contract['filename'], user_question)
                st.markdown(answer)
                if citations:
                    with st.expander("🔍 View Source Evidence"):
                        for c in citations:
                            st.markdown(f"**Page {c['page_number']}**: *\"{c['snippet']}\"*")

        save_chat_message(contract_id, "assistant", answer, citations)


if __name__ == "__main__":
    main()
