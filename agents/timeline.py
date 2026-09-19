"""
Agent 4 — Timeline Agent: Extract date milestones, 30-day alert calculations, and Plotly timeline chart.
"""
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from agents.extract import call_gemini_model, clean_json_text


def extract_timeline_events(pages_text: List[Dict[str, Any]], filename: str, extractions: Any = None) -> List[Dict[str, Any]]:
    """
    Extracts all date milestones (expiration, renewal, payment, notice windows, obligations).
    Calculates 30-day alerts based on current date.
    """
    full_document_text = "\n\n".join([f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages_text])

    prompt = f"""
You are a timeline extraction AI assistant. Extract all explicit date milestones, deadlines, renewal windows, payment due dates, and notice periods from this contract.

Contract Document: {filename}
{full_document_text}

Rules:
- NEVER invent or fabricate dates. Only extract explicit dates or clear relative deadlines (e.g. "30 days prior to Dec 31, 2026").
- If a date cannot be determined, DO NOT fabricate it.
- Format dates as YYYY-MM-DD whenever possible.

Return ONLY a JSON list of timeline event objects matching:
[
  {{
    "event_title": "Contract Expiration",
    "party": "Both Parties",
    "date_str": "2026-12-31",
    "event_type": "Expiration",
    "source_page": 1
  }}
]
Event types can be: Expiration, Renewal, Payment, Notice, Obligation, Milestone.
"""

    events = []
    try:
        response_text = call_gemini_model(prompt, json_mode=True)
        clean_json = clean_json_text(response_text)
        data = json.loads(clean_json)

        if isinstance(data, list):
            events = data
        elif isinstance(data, dict) and "events" in data:
            events = data["events"]
    except Exception as e:
        raise RuntimeError(f"Gemini Timeline Analysis Failed: {str(e)}")

    if not events:
        raise RuntimeError("Gemini did not return valid timeline events for this contract.")

    # Process alert levels
    return _process_event_alert_levels(events)


def _process_event_alert_levels(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    today = datetime.now().date()
    processed = []

    for ev in events:
        date_str = ev.get("date_str", "N/A")
        alert_level = "Upcoming"
        parsed_date = None

        # Attempt date parsing
        try:
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception:
            # Match formats like 2026-09-19 or Sep 19, 2026
            m = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
            if m:
                try:
                    parsed_date = datetime.strptime(m.group(1), "%Y-%m-%d").date()
                except Exception:
                    pass

        if parsed_date:
            days_diff = (parsed_date - today).days
            if days_diff < 0:
                alert_level = "Overdue"
            elif 0 <= days_diff <= 30:
                alert_level = "Due within 30 days"
            else:
                alert_level = "Upcoming"
        else:
            alert_level = "Upcoming"

        processed.append({
            "event_title": ev.get("event_title", "Milestone"),
            "party": ev.get("party", "General"),
            "date_str": date_str,
            "event_type": ev.get("event_type", "Milestone"),
            "source_page": int(ev.get("source_page", 1)),
            "alert_level": alert_level
        })

    return processed


def _heuristic_timeline_events(pages_text: List[Dict[str, Any]], extractions: Any = None) -> List[Dict[str, Any]]:
    events = []
    
    if extractions:
        eff = getattr(extractions, "effective_date", None)
        if eff and eff.value and eff.value != "Not found in contract":
            events.append({
                "event_title": "Contract Effective Date",
                "party": "All Parties",
                "date_str": eff.value,
                "event_type": "Milestone",
                "source_page": eff.source_page
            })
            
        exp = getattr(extractions, "expiration_date", None)
        if exp and exp.value and exp.value != "Not found in contract":
            events.append({
                "event_title": "Contract Expiration",
                "party": "All Parties",
                "date_str": exp.value,
                "event_type": "Expiration",
                "source_page": exp.source_page
            })

    if not events:
        # Default sample timeline milestone for visualization safety
        today_str = datetime.now().strftime("%Y-%m-%d")
        thirty_days = (datetime.now() + timedelta(days=25)).strftime("%Y-%m-%d")
        events = [
            {
                "event_title": "Effective Start Date",
                "party": "Vendor",
                "date_str": today_str,
                "event_type": "Milestone",
                "source_page": 1
            },
            {
                "event_title": "30-Day Contract Review Window",
                "party": "Client",
                "date_str": thirty_days,
                "event_type": "Notice",
                "source_page": 1
            }
        ]

    return events


def build_timeline_chart(events: List[Dict[str, Any]]) -> go.Figure:
    """Creates an interactive Plotly timeline chart."""
    if not events:
        fig = go.Figure()
        fig.update_layout(title="No Timeline Events Available")
        return fig

    # Prepare DataFrame-compatible records
    chart_data = []
    for ev in events:
        date_str = ev.get("date_str", "")
        parsed_dt = None
        try:
            parsed_dt = datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            m = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
            if m:
                try:
                    parsed_dt = datetime.strptime(m.group(1), "%Y-%m-%d")
                except Exception:
                    pass
        if not parsed_dt:
            parsed_dt = datetime.now()

        chart_data.append({
            "Event": ev["event_title"],
            "Party": ev["party"],
            "Date": parsed_dt,
            "Type": ev["event_type"],
            "Alert": ev["alert_level"],
            "Page": f"Page {ev['source_page']}"
        })

    color_map = {
        "Overdue": "#ef4444",           # Red
        "Due within 30 days": "#f97316", # Orange
        "Upcoming": "#10b981"            # Green
    }

    fig = px.scatter(
        chart_data,
        x="Date",
        y="Event",
        color="Alert",
        color_discrete_map=color_map,
        size_max=15,
        hover_data=["Party", "Type", "Page"],
        title="Interactive Contract Milestone Timeline"
    )

    fig.update_traces(marker=dict(size=14, symbol="diamond"))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Contract Event",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15, 23, 42, 0.6)",
        font=dict(color="#f8fafc"),
        height=380,
        margin=dict(l=20, r=20, t=50, b=20)
    )

    return fig
