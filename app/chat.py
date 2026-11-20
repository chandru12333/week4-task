
from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List
import re

from app.services.embeddings import generate_query_embedding
from app.services.vector_store import search_documents
from app.services.llm import (
    generate_answer,
    generate_answer_with_crm_tool,
    generate_answer_with_order_tools
)

router = APIRouter()

# Store conversation history
chat_history = {}


# Request validation
class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = "default"


# Response validation
class Source(BaseModel):
    file: str
    page: int


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    session_id: str


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    session_id = request.session_id

    # Get previous conversation
    if session_id not in chat_history:
        chat_history[session_id] = []

    history = chat_history[session_id][-5:]

    # Check whether PostgreSQL order tool is required
    order_answer = generate_answer_with_order_tools(request.message)
    if order_answer is not None:
        answer = order_answer
        sources = []
    else:
        # Check whether CRM tool is required
        crm_answer = generate_answer_with_crm_tool(request.message)
        if crm_answer is not None:
            answer = crm_answer
            sources = []
        else:
            # Convert question into embedding
            query_embedding = generate_query_embedding(
                request.message
            )

            # Search ChromaDB
            results = search_documents(query_embedding)

            documents = results["documents"][0]
            metadatas = results["metadatas"][0]
            distances = results["distances"][0]
            print("RETRIEVED DOCUMENTS:", documents)
            print("DISTANCES:", distances)

            # Check whether relevant content was found
            if not documents or distances[0] > 1.5:
                answer = "I don't know"
                sources = []

            else:
                # Build PDF context and sources
                context = ""
                sources = []

                for doc, metadata in zip(documents, metadatas):

                    context += doc + "\n\n"

                    page_match = re.search(
                        r"\[PAGE (\d+)\]",
                        doc
                    )

                    page_number = (
                        int(page_match.group(1))
                        if page_match else 1
                    )

                    source = {
                        "file": metadata.get("filename", "Unknown"),
                        "page": page_number
                    }

                    if source not in sources:
                        sources.append(source)

                # Build grounded prompt
                prompt = f"""
You are a document question answering assistant.

Answer the question using ONLY the context below.

If the answer is not available in the context,
reply exactly: I don't know

Previous conversation:
{history}

Document context:
{context}

Question:
{request.message}

Answer:
"""

                # Generate AI answer
                answer = generate_answer(prompt)

    # Save conversation
    chat_history[session_id].append({
        "role": "user",
        "content": request.message
    })

    chat_history[session_id].append({
        "role": "assistant",
        "content": answer
    })

    # Keep last 5 messages
    chat_history[session_id] = chat_history[session_id][-5:]

    return ChatResponse(
        answer=answer,
        sources=sources,
        session_id=session_id
    )
