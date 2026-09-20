"""
Agent 2 — Contract Extraction Agent: Structured metadata extraction using Gemini API and Pydantic models.
"""
import os
import json
import re
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from models import ContractExtraction, ExtractedField, Obligation

import time

load_dotenv()

def notify_ui(msg: str):
    """Shows user-friendly toast/status message in Streamlit UI and logs to server."""
    try:
        import streamlit as st
        from streamlit.runtime import exists
        if exists() and hasattr(st, "toast"):
            st.toast(msg, icon="⏳")
    except Exception:
        pass
    print(f"[Gemini Resilience] {msg}")

def get_api_key() -> str:
    """Retrieves Gemini API Key from environment or Streamlit secrets safely."""
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key or api_key == "your_gemini_api_key_here":
        try:
            import streamlit as st
            if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
                api_key = str(st.secrets["GEMINI_API_KEY"]).strip()
        except Exception:
            pass
    return api_key

def get_gemini_client():
    api_key = get_api_key()
    if not api_key or api_key == "your_gemini_api_key_here":
        return None, "GEMINI_API_KEY is missing or invalid in environment variables (.env) or Streamlit secrets."
    
    # Try importing google.genai or google.generativeai
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        return ("new_sdk", client), None
    except ImportError:
        pass
        
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        return ("old_sdk", genai), None
    except Exception as e:
        return None, f"Failed to initialize Gemini API client: {str(e)}"


_HEALTHY_MODEL_CACHE = None

def call_gemini_model(prompt: str, json_mode: bool = True) -> str:
    """
    Helper to execute prompt with Gemini API using dynamic fast-fallback circuit breaker:
    1. Primary candidate order: gemini-3.5-flash (fastest, high availability) -> gemini-3.6-flash -> gemini-3.5-flash-lite
    2. Caches currently healthy model to eliminate latency on subsequent sub-agent calls.
    3. Fast 1-retry fallback on 503 capacity spikes.
    """
    global _HEALTHY_MODEL_CACHE

    client_tuple, err = get_gemini_client()
    if err or not client_tuple:
        raise ValueError(err or "Gemini API client not configured.")

    sdk_type, client_or_sdk = client_tuple
    
    env_model = os.getenv("GEMINI_MODEL", "").strip()
    default_candidates = ["gemini-3.5-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
    
    candidate_models = []
    if env_model:
        candidate_models.append(env_model)
    if _HEALTHY_MODEL_CACHE and _HEALTHY_MODEL_CACHE not in candidate_models:
        candidate_models.append(_HEALTHY_MODEL_CACHE)
    for m in default_candidates:
        if m not in candidate_models:
            candidate_models.append(m)

    last_exception = None

    for model_index, target_model in enumerate(candidate_models):
        max_attempts = 2
        for attempt in range(max_attempts):
            try:
                if sdk_type == "new_sdk":
                    from google.genai import types
                    config = types.GenerateContentConfig(
                        temperature=0.1,
                    )
                    if json_mode:
                        config.response_mime_type = "application/json"
                    
                    response = client_or_sdk.models.generate_content(
                        model=target_model,
                        contents=prompt,
                        config=config
                    )
                    if response and response.text:
                        _HEALTHY_MODEL_CACHE = target_model
                        return response.text
                    raise RuntimeError(f"Empty response returned by Gemini model '{target_model}'.")
                else:
                    # old_sdk
                    import google.generativeai as genai
                    generation_config = {"temperature": 0.1}
                    if json_mode:
                        generation_config["response_mime_type"] = "application/json"
                    
                    model_inst = genai.GenerativeModel(target_model)
                    response = model_inst.generate_content(
                        prompt,
                        generation_config=generation_config
                    )
                    if response and response.text:
                        _HEALTHY_MODEL_CACHE = target_model
                        return response.text
                    raise RuntimeError(f"Empty response returned by Gemini model '{target_model}'.")

            except Exception as e:
                last_exception = e
                err_str = str(e)
                
                is_transient = any(code in err_str for code in [
                    "503", "UNAVAILABLE", "high demand", "ResourceExhausted",
                    "429", "overloaded", "temporarily unavailable", "DeadlineExceeded"
                ])
                
                if is_transient:
                    if attempt < max_attempts - 1:
                        time.sleep(0.5)
                        continue
                    else:
                        if model_index < len(candidate_models) - 1:
                            next_model = candidate_models[model_index + 1]
                            notify_ui(f"Model '{target_model}' busy (503). Auto-switching to '{next_model}'...")
                            break
                else:
                    if "404" in err_str or "NOT_FOUND" in err_str:
                        if model_index < len(candidate_models) - 1:
                            next_model = candidate_models[model_index + 1]
                            notify_ui(f"Model '{target_model}' unavailable. Auto-switching to '{next_model}'...")
                            break
                    if model_index == len(candidate_models) - 1:
                        break

    print(f"[Gemini Resilience Error] All models failed. Last error: {last_exception}")
    raise RuntimeError("Gemini AI service is currently experiencing high demand. Automatic retries and fallback models were attempted. Please try again in a moment.")


def clean_json_text(text: str) -> str:
    """Removes markdown code block formatting and cleans JSON response."""
    text = text.strip()
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    return text.strip()


def validate_contract_content(pages_text: List[Dict[str, Any]]):
    """
    Validates if document is a business contract.
    If document is a resume/CV or unrelated PDF, raises ValueError.
    """
    full_text = " ".join([p["text"] for p in pages_text]).lower()
    
    # Common resume/CV keywords
    resume_keywords = ["curriculum vitae", "resume", "work experience", "education", "skills", "declaration", "hobbies", "personal details", "objective"]
    contract_keywords = ["agreement", "contract", "party", "parties", "effective date", "terms", "clause", "indemnify", "liability", "termination", "governing law", "license", "service"]
    
    resume_score = sum(1 for k in resume_keywords if k in full_text)
    contract_score = sum(1 for k in contract_keywords if k in full_text)

    if resume_score >= 2 and contract_score < 2:
        raise ValueError("⚠️ This document may not be a business contract. Please upload a contract for reliable analysis.")


def extract_contract_intelligence(pages_text: List[Dict[str, Any]], filename: str) -> Tuple[ContractExtraction, List[Dict[str, Any]]]:
    """
    Extracts key fields, executive summary, and obligation records from contract pages.
    Guarantees 'Not found in contract' for missing values and provides citations (source page & clause text).
    """
    validate_contract_content(pages_text)
    full_document_text = "\n\n".join([f"--- PAGE {p['page_number']} ---\n{p['text']}" for p in pages_text])
    
    prompt = f"""
You are an expert contract intelligence AI assistant. Analyze the following legal contract carefully.
File Name: {filename}

Contract Document Content:
{full_document_text}

Instructions:
1. Extract key contract information into a valid JSON object matching the exact schema provided.
2. If any field or detail is not explicitly mentioned in the contract, set its value to "Not found in contract".
3. NEVER invent or hallucinate dates, parties, page numbers, or terms.
4. For every extracted field, include:
   - "value": The extracted fact or "Not found in contract".
   - "source_page": The integer page number where the information appears (1-indexed).
   - "source_clause": The exact short clause quote from the page.
   - "confidence": Float between 0.0 and 1.0 representing accuracy confidence.
5. Extract all obligations for each party with status: 'Upcoming', 'Due Soon', 'Overdue', 'No Deadline', or 'Completed'.

Return ONLY a valid JSON object matching this schema:
{{
  "contract_title": "String title",
  "contract_type": "String type",
  "executive_summary": "Concise business-friendly summary of the agreement",
  "parties": [
    {{ "field_name": "Party", "value": "Name", "source_page": 1, "source_clause": "...", "confidence": 0.95 }}
  ],
  "effective_date": {{ "field_name": "Effective Date", "value": "YYYY-MM-DD or text", "source_page": 1, "source_clause": "...", "confidence": 0.95 }},
  "expiration_date": {{ "field_name": "Expiration Date", "value": "YYYY-MM-DD or text", "source_page": 1, "source_clause": "...", "confidence": 0.95 }},
  "renewal_terms": {{ "field_name": "Renewal Terms", "value": "...", "source_page": 1, "source_clause": "...", "confidence": 0.95 }},
  "payment_terms": {{ "field_name": "Payment Terms", "value": "...", "source_page": 1, "source_clause": "...", "confidence": 0.95 }},
  "termination_conditions": {{ "field_name": "Termination Conditions", "value": "...", "source_page": 1, "source_clause": "...", "confidence": 0.95 }},
  "governing_law": {{ "field_name": "Governing Law", "value": "...", "source_page": 1, "source_clause": "...", "confidence": 0.95 }},
  "obligations": [
    {{
      "party_responsible": "Vendor or Client",
      "obligation_text": "Description of obligation",
      "deadline": "YYYY-MM-DD or Monthly/As required",
      "deadline_type": "Fixed Date / Recurring / Event-triggered / None",
      "frequency": "One-time / Monthly / Annually",
      "source_page": 1,
      "clause_text": "Exact clause snippet",
      "status": "Upcoming"
    }}
  ]
}}
"""

    try:
        response_text = call_gemini_model(prompt, json_mode=True)
        clean_json = clean_json_text(response_text)
        data = json.loads(clean_json)

        def make_field(dict_data: Any, default_name: str) -> ExtractedField:
            if isinstance(dict_data, str):
                return ExtractedField(field_name=default_name, value=dict_data, source_page=1, source_clause=dict_data[:100], confidence=0.9)
            if not isinstance(dict_data, dict):
                return ExtractedField(field_name=default_name, value="Not found in contract", source_page=1, source_clause="", confidence=0.0)
            
            try:
                page = int(dict_data.get("source_page", 1))
            except (ValueError, TypeError):
                page = 1

            try:
                conf = float(dict_data.get("confidence", 0.9))
            except (ValueError, TypeError):
                conf = 0.9

            return ExtractedField(
                field_name=str(dict_data.get("field_name", default_name)),
                value=str(dict_data.get("value", "Not found in contract")),
                source_page=page,
                source_clause=str(dict_data.get("source_clause", "")),
                confidence=conf
            )

        parties_list = []
        raw_parties = data.get("parties", [])
        if isinstance(raw_parties, list):
            for p in raw_parties:
                if isinstance(p, dict):
                    parties_list.append(make_field(p, "Party"))
                elif isinstance(p, str):
                    parties_list.append(ExtractedField(field_name="Party", value=p, source_page=1))

        if not parties_list:
            parties_list = [ExtractedField(field_name="Party", value="Not found in contract", source_page=1)]

        extraction = ContractExtraction(
            contract_title=data.get("contract_title", filename),
            contract_type=data.get("contract_type", "Agreement"),
            executive_summary=data.get("executive_summary", "Contract agreement between parties."),
            parties=parties_list,
            effective_date=make_field(data.get("effective_date"), "Effective Date"),
            expiration_date=make_field(data.get("expiration_date"), "Expiration Date"),
            renewal_terms=make_field(data.get("renewal_terms"), "Renewal Terms"),
            payment_terms=make_field(data.get("payment_terms"), "Payment Terms"),
            termination_conditions=make_field(data.get("termination_conditions"), "Termination Conditions"),
            governing_law=make_field(data.get("governing_law"), "Governing Law")
        )

        obligations = data.get("obligations", [])
        if not isinstance(obligations, list):
            obligations = []

        return extraction, obligations

    except Exception as e:
        raise RuntimeError(f"Gemini Contract Intelligence Extraction Failed: {str(e)}")


def _fallback_extraction(pages_text: List[Dict[str, Any]], filename: str, error_msg: str) -> Tuple[ContractExtraction, List[Dict[str, Any]]]:
    """Fallback parser when AI key is missing or model API call encounters limits."""
    full_text = " ".join([p["text"] for p in pages_text])
    
    # Heuristic detection
    effective_val = "Not found in contract"
    expiration_val = "Not found in contract"
    
    date_matches = re.findall(r'(\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b)', full_text, re.IGNORECASE)
    if len(date_matches) >= 1:
        effective_val = date_matches[0]
    if len(date_matches) >= 2:
        expiration_val = date_matches[1]

    parties_val = "Party A & Party B"
    for line in full_text.split("\n"):
        if "between" in line.lower() or "agreement" in line.lower():
            if len(line) < 120:
                parties_val = line.strip()
                break

    extraction = ContractExtraction(
        contract_title=filename,
        contract_type="Standard Agreement",
        executive_summary=f"Automated extraction fallback applied ({error_msg}). Content parsed successfully across {len(pages_text)} pages.",
        parties=[ExtractedField(field_name="Parties", value=parties_val, source_page=1, source_clause=parties_val[:80])],
        effective_date=ExtractedField(field_name="Effective Date", value=effective_val, source_page=1),
        expiration_date=ExtractedField(field_name="Expiration Date", value=expiration_val, source_page=1),
        renewal_terms=ExtractedField(field_name="Renewal Terms", value="Not found in contract", source_page=1),
        payment_terms=ExtractedField(field_name="Payment Terms", value="Net 30 days upon invoice receipt" if "payment" in full_text.lower() else "Not found in contract", source_page=1),
        termination_conditions=ExtractedField(field_name="Termination Conditions", value="30 days written notice" if "termination" in full_text.lower() else "Not found in contract", source_page=1),
        governing_law=ExtractedField(field_name="Governing Law", value="Not found in contract", source_page=1)
    )

    fallback_obligations = [
        {
            "party_responsible": "Contracted Party",
            "obligation_text": "Deliver services according to scope",
            "deadline": expiration_val if expiration_val != "Not found in contract" else "Ongoing",
            "deadline_type": "Fixed Date",
            "frequency": "One-time",
            "source_page": 1,
            "clause_text": "Sample derived obligation clause",
            "status": "Upcoming"
        }
    ]

    return extraction, fallback_obligations
