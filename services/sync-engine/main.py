from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import init_local_db, queue_offline_event, reconcile_pending_events

app = FastAPI(
    title="Sahakar-Link Sync Engine",
    description="Local Fabric Offline Event Queuing & Reconciliation Microservice",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    init_local_db()

class LocalEventRequest(BaseModel):
    event_type: str
    payload: dict

@app.post("/api/v1/sync/queue")
def record_local_event(request: LocalEventRequest):
    """Queues actions locally when offline."""
    event_id = queue_offline_event(request.event_type, request.payload)
    return {
        "status": "queued_offline",
        "event_id": event_id,
        "message": "Event safely stored in Local Fabric queue."
    }

@app.post("/api/v1/sync/reconcile")
def sync_now():
    """Trigger manual or automated synchronization once internet is restored."""
    result = reconcile_pending_events()
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=True)
