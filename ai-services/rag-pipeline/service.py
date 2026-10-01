import os
import httpx
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Environment Configuration
QDRANT_HOST = os.getenv("VECTOR_DB_URL", "http://localhost:6333")
QWEN_ENDPOINT = os.getenv("QWEN_LLM_ENDPOINT", "http://localhost:8001/v1/chat/completions")
COLLECTION_NAME = "sahakar_knowledge_base"

# Initialize Qdrant Client
qdrant = QdrantClient(url=QDRANT_HOST)

def init_vector_store():
    """Initializes the Qdrant collection for 1024-dim Nemotron Embeddings."""
    collections = qdrant.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)
    
    if not exists:
        qdrant.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=1024, # Standard vector dimension for Llama-Nemotron Embeddings
                distance=models.Distance.COSINE
            )
        )
        print(f"Collection '{COLLECTION_NAME}' created in Qdrant.")

async def retrieve_grounded_context(query_vector: list[float], top_k: int = 5) -> list[str]:
    """Retrieves relevant knowledge chunks from Qdrant vector database."""
    search_result = qdrant.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    # Extract payload content (documents/facts)
    return [hit.payload.get("text", "") for hit in search_result if hit.payload]

def generate_grounded_prompt(user_query: str, retrieved_docs: list[str]) -> str:
    """Formats prompt to restrict Qwen2.5-7B to retrieved factual evidence."""
    context_str = "\n---\n".join(retrieved_docs) if retrieved_docs else "No specific document context found."
    
    prompt = f"""You are the official Sahakar-Link Career & Learning Copilot.
Answer the user's question accurately using ONLY the provided verified context.
If the information cannot be verified from the context, state that clearly.

VERIFIED CONTEXT:
{context_str}

USER QUESTION:
{user_query}

ANSWER:"""
    return prompt

async def query_qwen_llm(prompt: str) -> str:
    """Calls Qwen2.5-7B-Instruct via OpenAI-compatible vLLM/Ollama API."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                QWEN_ENDPOINT,
                json={
                    "model": "Qwen/Qwen2.5-7B-Instruct",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.2 # Low temperature for bounded, factual answers
                },
                timeout=30.0
            )
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return f"AI Service Error: HTTP {response.status_code}"
        except Exception as e:
            # Fallback mock response for offline/testing phase
            return f"[Simulated Qwen2.5 Response]: Processed query based on {len(prompt)} prompt characters."
