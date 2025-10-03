import logging
from fastapi import Depends, APIRouter, HTTPException
from langchain.prompts import PromptTemplate
from langchain_community.llms import Ollama
from app.auth import get_current_user
from app.memory import ConversationMemory
from app.vectorstore import get_vectorstore

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize Ollama LLM
llm = Ollama(model="gemma:2b", temperature=0)

# Per-user memory storage
user_memories = {}

def get_user_memory(user_id: str):
    if user_id not in user_memories:
        user_memories[user_id] = ConversationMemory(max_turns=5)
    return user_memories[user_id]


@router.post("/api/chat")
async def chat_endpoint(
    body: dict,
    user_id: str = Depends(get_current_user),
):
    question = body.get("question")
    if not question:
        raise HTTPException(status_code=400, detail="Missing question")

    logger.info(f"User {user_id} asked: {question}")

    # Get vectorstore
    vs = get_vectorstore()

    # Retrieve relevant context
    docs = vs.similarity_search(question, k=3)
    sources = [{"source": doc.metadata.get("source", "")} for doc in docs]
    context_text = "\n\n".join(doc.page_content for doc in docs)

    # Retrieve conversation memory
    memory = get_user_memory(user_id)
    history_text = memory.get_history_text()

    # Prompt template
    template = """You are a helpful assistant.
Use the following context and conversation history to answer the question.
If you don't know, say you don't know.

Conversation history:
{history}

Context:
{context}

Question: {question}

Answer:"""

    prompt = PromptTemplate(
        input_variables=["history", "context", "question"],
        template=template,
    ).format(history=history_text, context=context_text, question=question)

    # Call Ollama
    try:
        res = llm.invoke(prompt)
        # Extract clean answer text
        answer_text = getattr(res, "content", None) or getattr(res, "response", None)
        if not answer_text:
            answer_text = str(res)
    except Exception as e:
        logger.error(f"LLM error: {e}")
        raise HTTPException(status_code=500, detail="LLM processing failed")

    # Save exchange in memory
    memory.add_exchange(question, answer_text)

    return {
        "question": question,
        "answer": answer_text.strip(),
        "sources": sources,
    }
