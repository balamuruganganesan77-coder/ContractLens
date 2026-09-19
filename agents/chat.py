"""
Agent 6 — RAG Contract Chat Agent: Grounded Q&A with strict ChromaDB vector retrieval and page citations.
"""
import json
from typing import List, Dict, Any, Tuple
from agents.ingest import search_contract_chunks
from agents.extract import call_gemini_model


def answer_contract_question(contract_id: str, filename: str, question: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Retrieves top relevant chunks from ChromaDB for the contract,
    prompts Gemini with strict grounding, and attaches source citations.
    """
    # 1. Retrieve top 4 relevant contract chunks from vector store
    retrieved_chunks = search_contract_chunks(contract_id, question, top_k=4)

    if not retrieved_chunks:
        fallback_msg = "I couldn't find enough evidence in the uploaded contract to answer this confidently."
        return fallback_msg, []

    # Format context for grounding
    context_str = ""
    citations = []
    for idx, chunk in enumerate(retrieved_chunks, 1):
        context_str += f"\n--- RETRIEVED EXCERPT {idx} (Page {chunk['page_number']}) ---\n{chunk['text']}\n"
        citations.append({
            "citation_id": idx,
            "page_number": chunk["page_number"],
            "snippet": chunk["text"][:300]
        })

    prompt = f"""
You are an evidence-based RAG Contract Q&A assistant for ContractLens.
Answer the user's question using ONLY the retrieved contract excerpts provided below.

File Name: {filename}

Retrieved Contract Context:
{context_str}

User Question: "{question}"

Strict Rules:
1. Base your answer strictly and exclusively on the retrieved contract context.
2. Every claim or fact in your response MUST explicitly cite its source page using the format:
   `[Source: Page X]` or `Source: Page X — [Section Name]`
3. If the retrieved context does NOT contain enough information or evidence to answer the question confidently, respond EXACTLY with:
   "I couldn't find enough evidence in the uploaded contract to answer this confidently."
4. NEVER fabricate clauses, terms, dates, or legal implications.
5. Provide a clear, professional, direct answer.
"""

    try:
        response_text = call_gemini_model(prompt, json_mode=False)
        answer = response_text.strip()
        
        # Verify grounding safety
        if not answer or len(answer) < 10:
            answer = "I couldn't find enough evidence in the uploaded contract to answer this confidently."
            
        return answer, citations

    except Exception as e:
        print(f"Contract Chat Gemini API Error: {e}")
        # Grounded fallback if API call fails
        fallback_answer = f"Based on retrieved excerpts on Page {retrieved_chunks[0]['page_number']}:\n\"{retrieved_chunks[0]['text'][:250]}...\"\n\nSource: Page {retrieved_chunks[0]['page_number']} — Clause Context."
        return fallback_answer, citations
