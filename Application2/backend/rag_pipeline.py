"""
RAG pipeline module:
- uses HuggingFace MiniLM embeddings (fast)
- uses langchain_milvus Milvus wrapper
- uses Ollama LLM (llama2:7b-chat-q4) for responses
- provides ask (sync) and ask_stream (generator) interfaces
"""

from typing import List, Dict
from database import create_or_get_collection
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus  # use the langchain-milvus package
from langchain_community.llms import Ollama  # Ollama wrapper
import os

COL_NAME = os.getenv("MILVUS_COLLECTION", "rag_docs")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
LLM_MODEL = os.getenv("LLM_MODEL", "llama2:7b-chat-q4")

class RAGPipeline:
    def __init__(self):
        # ensure Milvus collection exists (create if missing)
        self.collection = create_or_get_collection(drop_if_exists=False)

        # embeddings
        self.emb = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

        # vector store wrapper (langchain-milvus)
        self.vs = Milvus(
            embedding_function=self.emb,
            collection_name=self.collection.name,
            connection_args={"host": os.getenv("MILVUS_HOST", "127.0.0.1"), "port": os.getenv("MILVUS_PORT", "19530")},
            text_field="text",
            vector_field="embedding",
            auto_id=True,
        )

        # llm
        self.llm = Ollama(model=LLM_MODEL)

        print("✅ RAGPipeline ready. collection:", self.collection.name)

    def _build_prompt(self, question: str, chunks: List[str]) -> str:
        context = "\n\n".join(chunks) if chunks else ""
        template = (
            "You are a meticulous and accurate document analyst. Your task is to answer the user's question based exclusively on the provided context. "
            "Follow these rules strictly:\n"
            "1. Your entire response must be grounded in the facts provided in the 'Context' section. Do not use any prior knowledge.\n"
            "2. If multiple parts of the context are relevant, synthesize them into a single, coherent answer.\n"
            "3. If the context does not contain the information needed to answer the question, you must state only: "
            "'The provided context does not contain enough information to answer this question.'\n"
            "-----------------------------------------\n"
            f"Context: {context}\n"
            "-----------------------------------------\n"
            f"Question: {question}\n\n"
            "Answer:"
        )
        return template

    def retrieve(self, query: str, k: int = 3) -> List[Dict]:
        """
        Return top-k matching docs as list of {"text","source"}.
        """
        docs = self.vs.similarity_search(query, k=k)
        hits = []
        for d in docs:
            hits.append({"text": d.page_content, "source": d.metadata.get("source", "")})
        return hits

    def ask(self, user_id: str, question: str) -> Dict:
        """
        Synchronous call that returns answer + sources.
        """
        hits = self.retrieve(question, k=3)
        chunks = [h["text"] for h in hits]
        prompt = self._build_prompt(question, chunks)
        answer = self.llm(prompt)
        return {"question": question, "answer": answer, "sources": [{"source": h["source"]} for h in hits]}

    def ask_stream(self, user_id: str, question: str):
        """
        Generator that yields string chunks from the LLM stream.
        """
        hits = self.retrieve(question, k=3)
        chunks = [h["text"] for h in hits]
        prompt = self._build_prompt(question, chunks)
        # Ollama stream yields strings (depends on wrapper)
        for chunk in self.llm.stream(prompt):
            yield chunk