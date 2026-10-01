import sqlite3
import json
import uuid
import datetime
import os
import psycopg2
from psycopg2.extras import RealDictCursor

LOCAL_DB_FILE = "local_fabric.db"
POSTGRES_URL = os.getenv("DATABASE_URL", "postgresql://sahakar:sahakar_dev_password@localhost:5432/sahakar_link")

def init_local_db():
    """Initializes the edge SQLite database for offline event queuing."""
    conn = sqlite3.connect(LOCAL_DB_FILE)
    cursor = conn.cursor()
    
    # Offline Event Queue Table (Append-Only Log)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS offline_event_queue (
            event_id TEXT PRIMARY KEY,
            event_type TEXT NOT NULL, -- e.g., 'ATTENDANCE_MARKED', 'ASSESSMENT_SUBMITTED'
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            is_synced INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("Local Fabric SQLite Engine Initialized.")

def queue_offline_event(event_type: str, payload: dict) -> str:
    """Queues an event locally when internet connectivity is unavailable."""
    conn = sqlite3.connect(LOCAL_DB_FILE)
    cursor = conn.cursor()
    
    event_id = str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    cursor.execute("""
        INSERT INTO offline_event_queue (event_id, event_type, payload, created_at, is_synced)
        VALUES (?, ?, ?, ?, 0)
    """, (event_id, event_type, json.dumps(payload), created_at))
    
    conn.commit()
    conn.close()
    return event_id

def reconcile_pending_events() -> dict:
    """Reconciles pending offline events from SQLite queue to central PostgreSQL database."""
    conn = sqlite3.connect(LOCAL_DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT event_id, event_type, payload, created_at FROM offline_event_queue WHERE is_synced = 0")
    pending_events = cursor.fetchall()
    
    if not pending_events:
        conn.close()
        return {"status": "success", "synced_count": 0, "message": "No pending events to sync."}
        
    synced_ids = []
    failed_count = 0
    
    try:
        # Connect to Central PostgreSQL Database
        pg_conn = psycopg2.connect(POSTGRES_URL)
        pg_cursor = pg_conn.cursor()
        
        for event_id, event_type, payload_str, created_at in pending_events:
            payload = json.loads(payload_str)
            
            if event_type == "ATTENDANCE_MARKED":
                pg_cursor.execute("""
                    INSERT INTO attendance_records (id, student_id, batch_id, method, liveness_score, is_offline_sync, synced_at)
                    VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
                    ON CONFLICT (id) DO NOTHING
                """, (
                    payload.get("record_id", str(uuid.uuid4())),
                    payload.get("student_id"),
                    payload.get("batch_id"),
                    payload.get("method", "FACE_ADA_FACE"),
                    payload.get("liveness_score", 1.0)
                ))
                synced_ids.append(event_id)
                
        pg_conn.commit()
        pg_cursor.close()
        pg_conn.close()
        
        # Mark local events as synced
        for event_id in synced_ids:
            cursor.execute("UPDATE offline_event_queue SET is_synced = 1 WHERE event_id = ?", (event_id,))
        conn.commit()
        
    except Exception as e:
        print(f"Reconciliation Warning/Error: {e}")
        failed_count += 1
        
    conn.close()
    return {
        "status": "success" if failed_count == 0 else "partial_failure",
        "synced_count": len(synced_ids),
        "failed_count": failed_count
    }
