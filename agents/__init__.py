"""
ContractLens Agent Subpackage
"""
from .ingest import ingest_pdf, search_contract_chunks, get_all_chunks_for_contract
from .extract import extract_contract_intelligence
from .risk import detect_contract_risks
from .timeline import extract_timeline_events, build_timeline_chart
from .compare import compare_contract_versions
from .chat import answer_contract_question

__all__ = [
    "ingest_pdf",
    "search_contract_chunks",
    "get_all_chunks_for_contract",
    "extract_contract_intelligence",
    "detect_contract_risks",
    "extract_timeline_events",
    "build_timeline_chart",
    "compare_contract_versions",
    "answer_contract_question",
]
