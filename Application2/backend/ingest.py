"""
Simple ingestion utility to read files from RAGData/ and insert into Milvus.
Supports .txt and .pdf. Splits long text into chunks.

Usage:
    python3 ingest.py
"""

import os
from database import create_or_get_collection
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus
from typing import List

# optional: pdf reader
try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

CHUNK_SIZE = 600   # characters per chunk (adjust)
OVERLAP = 100

DATA_DIR = os.getenv("RAG_DATA_DIR", "RAGData")

def read_txt(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()

def read_pdf(path: str) -> str:
    if PdfReader is None:
        raise RuntimeError("PyPDF2 not installed (pip install PyPDF2)")
    reader = PdfReader(path)
    texts = []
    for page in reader.pages:
        texts.append(page.extract_text() or "")
    return "\n".join(texts)

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = OVERLAP) -> List[str]:
    if not text:
        return []
    chunks = []
    start = 0
    length = len(text)
    while start < length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = max(end - overlap, end)
    return chunks

def ingest_folder(folder: str = DATA_DIR):
    coll = create_or_get_collection(drop_if_exists=False)
    emb = HuggingFaceEmbeddings(model_name=os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2"))
    vs = Milvus(
        embedding_function=emb,
        collection_name=coll.name,
        connection_args={"host": os.getenv("MILVUS_HOST", "127.0.0.1"), "port": os.getenv("MILVUS_PORT", "19530")},
        text_field="text",
        vector_field="embedding",
        auto_id=True,
    )

    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    inserted = 0
    for fname in files:
        path = os.path.join(folder, fname)
        ext = os.path.splitext(fname)[1].lower()
        try:
            if ext == ".txt":
                text = read_txt(path)
            elif ext == ".pdf":
                text = read_pdf(path)
            else:
                continue
        except Exception as e:
            print(f"Failed to read {path}: {e}")
            continue

        chunks = chunk_text(text)
        to_add_texts = chunks
        to_add_metadatas = [{"source": fname} for _ in chunks]
        if to_add_texts:
            vs.add_texts(texts=to_add_texts, metadatas=to_add_metadatas)
            inserted += len(to_add_texts)
            print(f"Inserted {len(to_add_texts)} chunks from {fname}")

    print(f"Finished ingest. Total chunks inserted: {inserted}")

if __name__ == "__main__":
    ingest_folder()