"""
Agent 5 — Version Compare Agent: Python difflib textual diffing + Gemini business impact explanations.
"""
import difflib
import json
import fitz  # PyMuPDF
from typing import List, Dict, Any, Tuple
from agents.extract import call_gemini_model, clean_json_text


def extract_pdf_pages(pdf_bytes: bytes) -> List[Dict[str, Any]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = []
    for i in range(len(doc)):
        text = doc.load_page(i).get_text("text") or ""
        pages.append({"page_number": i + 1, "text": text.strip()})
    doc.close()
    return pages


def compare_contract_versions(v1_bytes: bytes, v1_filename: str, v2_bytes: bytes, v2_filename: str) -> List[Dict[str, Any]]:
    """
    Compares V1 and V2 contract PDF files using Python difflib for exact text differences,
    and Gemini AI to explain operational & financial business impacts.
    """
    v1_pages = extract_pdf_pages(v1_bytes)
    v2_pages = extract_pdf_pages(v2_bytes)

    v1_full_text = "\n\n".join([f"[V1 Page {p['page_number']}]\n{p['text']}" for p in v1_pages])
    v2_full_text = "\n\n".join([f"[V2 Page {p['page_number']}]\n{p['text']}" for p in v2_pages])

    # Perform line-by-line diffing with difflib
    v1_lines = v1_full_text.splitlines()
    v2_lines = v2_full_text.splitlines()

    differ = difflib.SequenceMatcher(None, v1_lines, v2_lines)
    diff_blocks = []

    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag == "equal":
            continue
            
        v1_chunk = "\n".join(v1_lines[i1:i2]).strip()
        v2_chunk = "\n".join(v2_lines[j1:j2]).strip()
        
        if not v1_chunk and not v2_chunk:
            continue

        change_type = "Modified"
        if tag == "insert":
            change_type = "Added"
        elif tag == "delete":
            change_type = "Removed"

        diff_blocks.append({
            "change_type": change_type,
            "v1_text": v1_chunk[:500],
            "v2_text": v2_chunk[:500],
            "line_range_v1": f"{i1+1}-{i2}",
            "line_range_v2": f"{j1+1}-{j2}"
        })

    # Limit diff blocks for API prompt to top meaningful changes
    significant_diffs = diff_blocks[:10]
    if not significant_diffs:
        return []

    prompt = f"""
You are a senior business analyst AI. You are provided with exact textual differences between Version 1 ({v1_filename}) and Version 2 ({v2_filename}) of a contract.

Identified Textual Differences:
{json.dumps(significant_diffs, indent=2)}

Instructions:
1. For each difference block, identify the contract clause/topic (e.g. Payment Terms, Termination Notice, Indemnity Cap).
2. Explain the BUSINESS IMPACT (operational, financial, risk profile, cash-flow timing) of this change for non-legal stakeholders.
3. DO NOT provide legal conclusions or state whether a clause is legally binding.
4. Keep the textual difference distinctly separated from your AI business impact explanation.

Return ONLY a JSON array matching:
[
  {{
    "clause_name": "Payment Terms & Invoicing Window",
    "change_type": "Modified",
    "v1_text": "Payment shall be due within 30 days of invoice receipt.",
    "v2_text": "Payment shall be due within 15 days of invoice receipt.",
    "business_impact": "Cash-flow timing will accelerate. The company must process payments 15 days faster to avoid late fees.",
    "source_page": "V1 Page 2 -> V2 Page 2"
  }}
]
"""

    try:
        response_text = call_gemini_model(prompt, json_mode=True)
        clean_json = clean_json_text(response_text)
        data = json.loads(clean_json)

        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "comparisons" in data:
            return data["comparisons"]
        raise ValueError("Unexpected JSON response format returned by Gemini for version comparison.")
    except Exception as e:
        raise RuntimeError(f"Gemini Version Comparison Analysis Failed: {str(e)}")
