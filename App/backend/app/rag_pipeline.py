import os
import logging
from collections import defaultdict
from typing import List, Dict, Iterable

from .database import create_or_get_collection
from .config import settings
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_milvus import Milvus

# Ollama (or swap for your LLM client)
try:
    from ollama import Client as OllamaClient
    _OLLAMA_AVAILABLE = True
except Exception:
    _OLLAMA_AVAILABLE = False

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self):
        self.collection = create_or_get_collection(drop_if_exists=False)
        self.emb = HuggingFaceEmbeddings(model_name=settings.EMBED_MODEL)
        self.vs = Milvus(
            embedding_function=self.emb,
            collection_name=self.collection.name,
            connection_args={"host": settings.MILVUS_HOST, "port": settings.MILVUS_PORT},
            text_field="text",
            vector_field="embedding",
            auto_id=True,
        )
        self.top_k = settings.TOP_K
        self.histories = defaultdict(list)  # user_id -> list of (q, a)
        if _OLLAMA_AVAILABLE:
            self.llm = OllamaClient()
            self.llm_model = settings.LLM_MODEL
        else:
            self.llm = None
            self.llm_model = None
            logger.warning("Ollama client not available. Replace LLM calls accordingly.")

    def retrieve(self, query: str, k: int = None) -> List[Dict]:
        k = k or self.top_k
        docs = self.vs.similarity_search(query, k=k)
        hits = []
        for d in docs:
            meta = d.metadata or {}
            src = meta.get("source", "")
            if src:
                src = f"/files/{os.path.basename(src)}"
            hits.append({"text": d.page_content, "source": src})
        return hits

    def _build_prompt(self, user_id: str, question: str, chunks: List[str]) -> str:
        # Last up to 5 exchanges
        history = self.histories.get(user_id, [])[-5:]
        hist_str = ""
        for q, a in history:
            hist_str += f"User: {q}\nAssistant: {a}\n"

        context = "\n\n".join(chunks) if chunks else ""
        prompt = (
            "You are an assistant that MUST answer using ONLY the provided context. "
            "If the context does not contain the answer, reply: 'The provided context does not contain enough information.'\n\n"
            f"Conversation history:\n{hist_str}\n"
            f"Context:\n{context}\n\n"
            f"User: {question}\nAssistant:"
        )
        return prompt

    def _call_llm(self, prompt: str) -> str:
        if _OLLAMA_AVAILABLE and self.llm is not None:
            try:
                # Use Ollama generate (responses may vary depending on client)
                res = self.llm.generate(model=self.llm_model, prompt=prompt)
                # Ollama returns dict-like with choices; adapt as needed
                if isinstance(res, dict):
                    choices = res.get("choices", [])
                    if choices:
                        return choices[0].get("content", "").strip()
                # fallback
                return str(res).strip()
            except Exception as e:
                logger.exception("LLM call failed: %s", e)
                return "LLM inference failed."
        else:
            # No LLM configured — return a placeholder
            logger.warning("No LLM client configured; returning placeholder.")
            return "LLM not configured on server. Please configure Ollama or another LLM client."

    def ask(self, user_id: str, question: str, top_k: int = None) -> Dict:
        hits = self.retrieve(question, k=top_k or self.top_k)
        chunks = [h["text"] for h in hits]
        prompt = self._build_prompt(user_id, question, chunks)
        answer = self._call_llm(prompt)

        # Save to per-user history (keep last 5)
        self.histories[user_id].append((question, answer))
        if len(self.histories[user_id]) > 5:
            self.histories[user_id] = self.histories[user_id][-5:]

        return {"question": question, "answer": answer, "sources": [{"source": h["source"]} for h in hits]}

    def ask_stream(self, user_id: str, question: str, top_k: int = None) -> Iterable[str]:
        # If LLM supports streaming, implement it here. As a fallback yield full answer at end.
        hits = self.retrieve(question, k=top_k or self.top_k)
        chunks = [h["text"] for h in hits]
        prompt = self._build_prompt(user_id, question, chunks)

        if _OLLAMA_AVAILABLE and hasattr(self.llm, "stream"):
            try:
                for piece in self.llm.stream(model=self.llm_model, prompt=prompt):
                    yield piece
                return
            except Exception as e:
                logger.exception("LLM streaming failed: %s", e)
        # fallback
        answer = self._call_llm(prompt)
        self.histories[user_id].append((question, answer))
        if len(self.histories[user_id]) > 5:
            self.histories[user_id] = self.histories[user_id][-5:]
        yield answer
