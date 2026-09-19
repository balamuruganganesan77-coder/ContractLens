"""
Agent 3 — Risk Agent: Automated detection of risky contract clauses (Liability, Auto-renewal, Termination, Penalties).
"""
import json
from typing import List, Dict, Any
from agents.extract import call_gemini_model, clean_json_text

RISK_CATEGORIES = [
    "Auto-renewal",
    "Unlimited liability",
    "High penalties",
    "Unilateral termination",
    "Short termination notice",
    "Ambiguous obligations",
    "Missing important dates",
    "Unusual payment terms",
    "Strong indemnification clauses"
]

def detect_contract_risks(pages_text: List[Dict[str, Any]], filename: str) -> List[Dict[str, Any]]:
    """
    Scans contract pages for high/medium/low risk flags and returns structured risk items
    with source page citations, exact clause snippets, and human review recommendations.
    """
    full_document_text = "\n\n".join([f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages_text])

    prompt = f"""
You are an expert contract risk analyst AI assistant. Analyze the contract text below for dangerous, ambiguous, or one-sided business terms requiring human legal review.

Contract Document: {filename}
{full_document_text}

Scan for at least the following categories of risk:
1. Auto-renewal (automatic lock-in or short opt-out window)
2. Unlimited liability (uncapped damages or absence of liability caps)
3. High penalties (liquidated damages, late payment penalties > 1.5%/month)
4. Unilateral termination (one party can terminate without cause, other cannot)
5. Short termination notice (< 30 days notice required)
6. Ambiguous obligations (vague standard of performance)
7. Missing important dates (missing expiration date or milestone timelines)
8. Unusual payment terms (upfront 100% payment, non-refundable retainers)
9. Strong indemnification clauses (broad hold harmless obligations)

Instructions:
- Return ONLY a JSON array of risk objects.
- For each risk found, provide:
  - "risk_title": Short descriptive title
  - "severity": "High", "Medium", or "Low"
  - "reason": Clear business explanation of the risk impact
  - "source_page": Integer page number (1-indexed)
  - "clause_text": Verbatim excerpt of the clause
  - "action_recommended": Concrete human review action item

Example Schema:
[
  {{
    "risk_title": "Unlimited Liability Clause",
    "severity": "High",
    "reason": "Section 8 contains no limitation on consequential damages, exposing the business to uncapped financial risk.",
    "source_page": 4,
    "clause_text": "Neither party shall limit its liability for indirect, special, or consequential damages...",
    "action_recommended": "Human Review Recommended: Propose a total liability cap equal to 12 months of fees paid."
  }}
]
"""

    try:
        response_text = call_gemini_model(prompt, json_mode=True)
        clean_json = clean_json_text(response_text)
        data = json.loads(clean_json)

        if isinstance(data, list):
            return _format_risks(data)
        elif isinstance(data, dict) and "risks" in data:
            return _format_risks(data["risks"])
        raise ValueError("Unexpected JSON response format returned by Gemini for risk analysis.")

    except Exception as e:
        raise RuntimeError(f"Gemini Risk Analysis Failed: {str(e)}")


def _format_risks(raw_risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    formatted = []
    for r in raw_risks:
        action = r.get("action_recommended", "Human Review Recommended: Evaluate with legal counsel.")
        if "Human Review Recommended" not in action:
            action = f"Human Review Recommended: {action}"
            
        formatted.append({
            "risk_title": r.get("risk_title", "Contract Risk Flag"),
            "severity": r.get("severity", "Medium") if r.get("severity") in ["High", "Medium", "Low"] else "Medium",
            "reason": r.get("reason", "Potential adverse contract condition detected."),
            "source_page": int(r.get("source_page", 1)),
            "clause_text": r.get("clause_text", "Clause excerpt unavailable."),
            "action_recommended": action
        })
    return formatted


def _heuristic_risk_detector(pages_text: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Heuristic risk scanner used when LLM call is unavailable."""
    risks = []
    
    for page in pages_text:
        text = page["text"]
        text_lower = text.lower()
        page_num = page["page_number"]

        if "auto-renew" in text_lower or "automatically renew" in text_lower:
            risks.append({
                "risk_title": "Automatic Renewal Lock-In",
                "severity": "High",
                "reason": "Agreement automatically renews unless written notice is served in advance.",
                "source_page": page_num,
                "clause_text": _get_snippet(text, ["auto-renew", "automatically renew"]),
                "action_recommended": "Human Review Recommended: Calendar opt-out notice deadline immediately."
            })

        if "indemnin" in text_lower or "hold harmless" in text_lower:
            risks.append({
                "risk_title": "Broad Indemnification Obligation",
                "severity": "Medium",
                "reason": "Indemnification clause may impose duty to defend legal claims against counterpart.",
                "source_page": page_num,
                "clause_text": _get_snippet(text, ["indemnify", "hold harmless"]),
                "action_recommended": "Human Review Recommended: Verify indemnity is mutual and capped."
            })

        if "unlimited" in text_lower or "without limitation" in text_lower or "consequential damages" in text_lower:
            risks.append({
                "risk_title": "Liability Exposure / Uncapped Damages",
                "severity": "High",
                "reason": "Contains terms referencing uncapped or broad damages exposure.",
                "source_page": page_num,
                "clause_text": _get_snippet(text, ["unlimited", "consequential", "without limitation"]),
                "action_recommended": "Human Review Recommended: Insert standard liability cap equal to contract value."
            })

        if "terminate at any time" in text_lower or "terminate for convenience" in text_lower:
            risks.append({
                "risk_title": "Unilateral Termination Rights",
                "severity": "Medium",
                "reason": "Contract allows termination for convenience without cause.",
                "source_page": page_num,
                "clause_text": _get_snippet(text, ["terminate", "convenience"]),
                "action_recommended": "Human Review Recommended: Ensure mutual notice period of at least 30-60 days."
            })

    if not risks:
        risks.append({
            "risk_title": "Missing Explicit Date Safeguards",
            "severity": "Low",
            "reason": "No explicit high-risk penalty clauses identified in heuristic pass.",
            "source_page": 1,
            "clause_text": "Standard agreement terms scan complete.",
            "action_recommended": "Human Review Recommended: Standard legal check recommended."
        })

    return risks


def _get_snippet(text: str, keywords: List[str]) -> str:
    for line in text.split("\n"):
        if any(k in line.lower() for k in keywords):
            return line.strip()[:150]
    return text[:150].strip()
