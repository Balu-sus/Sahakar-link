from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service import init_vector_store, retrieve_grounded_context, generate_grounded_prompt, query_qwen_llm

app = FastAPI(
    title="Sahakar-Link RAG Pipeline Service",
    description="Vector Search, Nemotron Reranking, and Grounded Qwen2.5 Generation Engine",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    try:
        init_vector_store()
    except Exception as e:
        print(f"Vector DB initialization warning: {e}")

class RAGQueryRequest(BaseModel):
    user_id: str
    query: str
    # Dummy embedding for testing endpoint structure
    dummy_vector: list[float] = [0.1] * 1024 

@app.post("/api/v1/rag/ask")
async def ask_copilot(request: RAGQueryRequest):
    # 1. Retrieve grounded contexts from Vector DB
    docs = await retrieve_grounded_context(request.dummy_vector, top_k=3)
    
    # 2. Build Bounded RAG Prompt
    prompt = generate_grounded_prompt(request.query, docs)
    
    # 3. Call Qwen2.5 LLM
    answer = await query_qwen_llm(prompt)
    
    return {
        "status": "success",
        "user_id": request.user_id,
        "retrieved_sources_count": len(docs),
        "response": answer
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
