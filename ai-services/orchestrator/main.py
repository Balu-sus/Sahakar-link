from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Sahakar-Link AI Orchestrator",
    description="Central routing gateway for Qwen2.5-7B, RAG, IndicTrans2, and Biometrics",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    user_id: str
    query: str
    language: str = "en"

@app.get("/")
def health_check():
    return {"status": "online", "service": "AI Orchestrator"}

@app.post("/api/v1/ai/query")
async def route_ai_request(request: QueryRequest):
    # Route logic for RAG -> Qwen -> IndicTrans2 translation
    return {
        "status": "success",
        "routing": "RAG_Pipeline",
        "input_language": request.language,
        "response": f"Processed query: {request.query}"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
