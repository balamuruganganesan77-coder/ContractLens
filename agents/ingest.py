"""
Agent 1 — Ingestion Agent: PDF parsing with PyMuPDF, chunking, and ChromaDB vector indexing.
"""
import os
import fitz  # PyMuPDF
import chromadb
from typing import List, Dict, Any, Tuple

CHROMA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")

# Simple memory storage fallback if ChromaDB fails
_MEMORY_CHUNKS: List[Dict[str, Any]] = []


def get_chroma_client():
    os.makedirs(CHROMA_DIR, exist_ok=True)
    try:
        return chromadb.PersistentClient(path=CHROMA_DIR)
    except Exception as e:
        print(f"Warning: ChromaDB PersistentClient initialization issue: {e}")
        return None


def get_chroma_collection():
    client = get_chroma_client()
    if client:
        try:
            return client.get_or_create_collection(
                name="contract_chunks",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            print(f"Warning: ChromaDB collection retrieval error: {e}")
    return None


def ingest_pdf(pdf_bytes: bytes, filename: str, contract_id: str) -> Tuple[List[Dict[str, Any]], int]:
    """
    Parses PDF using PyMuPDF, extracts text with page numbers preserved,
    splits content into meaningful chunks, and stores metadata + vector records in ChromaDB.
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    chunks = []
    chunk_index = 0

    for page_num in range(len(doc)):
        try:
            page = doc.load_page(page_num)
            text = page.get_text("text") or ""
        except Exception as e:
            print(f"Warning: page {page_num+1} load error: {e}")
            text = ""
        clean_text = text.strip()
        
        pages_text.append({
            "page_number": page_num + 1,
            "text": clean_text
        })

        if not clean_text:
            continue

        # Split page content into paragraphs/chunks
        paragraphs = clean_text.split("\n\n")
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            if len(current_chunk) + len(para) < 800:
                current_chunk += " " + para if current_chunk else para
            else:
                chunk_index += 1
                chunks.append({
                    "chunk_id": f"{contract_id}_chunk_{chunk_index}",
                    "contract_id": contract_id,
                    "filename": filename,
                    "page_number": page_num + 1,
                    "text": current_chunk.strip()
                })
                current_chunk = para

        if current_chunk:
            chunk_index += 1
            chunks.append({
                "chunk_id": f"{contract_id}_chunk_{chunk_index}",
                "contract_id": contract_id,
                "filename": filename,
                "page_number": page_num + 1,
                "text": current_chunk.strip()
            })

    doc.close()

    # Index into ChromaDB
    collection = get_chroma_collection()
    if collection and chunks:
        documents = [c["text"] for c in chunks]
        metadatas = [
            {
                "contract_id": c["contract_id"],
                "filename": c["filename"],
                "page_number": c["page_number"],
                "chunk_id": c["chunk_id"]
            }
            for c in chunks
        ]
        ids = [c["chunk_id"] for c in chunks]
        try:
            # Delete any previous chunks for this contract to prevent duplicates
            try:
                collection.delete(where={"contract_id": contract_id})
            except Exception:
                pass
                
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        except Exception as e:
            print(f"ChromaDB indexing fallback warning: {e}")

    # Keep memory backup
    global _MEMORY_CHUNKS
    _MEMORY_CHUNKS = [c for c in _MEMORY_CHUNKS if c.get("contract_id") != contract_id]
    _MEMORY_CHUNKS.extend(chunks)

    return pages_text, len(chunks)


def search_contract_chunks(contract_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Search ChromaDB for relevant contract text chunks matching the query.
    """
    collection = get_chroma_collection()
    results = []

    if collection:
        try:
            res = collection.query(
                query_texts=[query],
                n_results=top_k,
                where={"contract_id": contract_id}
            )
            if res and "documents" in res and res["documents"]:
                docs = res["documents"][0]
                metas = res["metadatas"][0] if "metadatas" in res else []
                for i in range(len(docs)):
                    meta = metas[i] if i < len(metas) else {}
                    results.append({
                        "text": docs[i],
                        "page_number": meta.get("page_number", 1),
                        "contract_id": meta.get("contract_id", contract_id),
                        "filename": meta.get("filename", "")
                    })
                return results
        except Exception as e:
            print(f"ChromaDB search warning: {e}")

    # Fallback to simple keyword memory matching
    query_lower = query.lower()
    matching_chunks = []
    for c in _MEMORY_CHUNKS:
        if c.get("contract_id") == contract_id:
            score = sum(1 for word in query_lower.split() if word in c["text"].lower())
            matching_chunks.append((score, c))
            
    matching_chunks.sort(key=lambda x: x[0], reverse=True)
    for score, c in matching_chunks[:top_k]:
        results.append({
            "text": c["text"],
            "page_number": c.get("page_number", 1),
            "contract_id": contract_id,
            "filename": c.get("filename", "")
        })

    return results


def get_all_chunks_for_contract(contract_id: str) -> List[Dict[str, Any]]:
    """Retrieve all chunks for a contract."""
    return [c for c in _MEMORY_CHUNKS if c.get("contract_id") == contract_id]
