from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import pathlib

app = FastAPI(
    title="Sahakar-Link Service",
    description="Cooperative Platform & Copilot Adapter",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UI_PATH = pathlib.Path(__file__).parent / "templates" / "index.html"

@app.get("/", response_class=HTMLResponse, tags=["UI"])
async def read_root():
    """Serves the SAHAKAR-LINK full UI dashboard interface."""
    if UI_PATH.exists():
        return HTMLResponse(content=UI_PATH.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>UI Template Not Found</h1>", status_code=404)

@app.post("/api/v1/copilot")
async def copilot_support(payload: dict):
    question = payload.get("question", "").lower()
    
    if "rest" in question or "api" in question:
        answer = (
            "<b>REST APIs (Representational State Transfer)</b> allow client applications to interact with backend services through standard HTTP protocols.<br><br>"
            "<b>Key Concepts for Python Full Stack:</b><br>"
            "• <b>GET:</b> Retrieve data from the server.<br>"
            "• <b>POST:</b> Send new data to create a resource.<br>"
            "• <b>PUT/PATCH:</b> Update an existing resource.<br>"
            "• <b>DELETE:</b> Remove a resource.<br><br>"
            "In Python, frameworks like FastAPI and Flask are used to define REST endpoints that send and receive JSON data."
        )
    else:
        answer = f"Here is context regarding your query <i>'{payload.get('question')}'</i>: Your learning pathway covers core principles, practical exercises, and secure module assessments."

    return {"status": "success", "response": answer}

