from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3

from backend.agents.orchestrator import handle_user_query
from backend.agents.analytics import ANALYTICS_DB_PATH, update_device_status
from backend.database import init_db

app = FastAPI(title="Grocery Multi-Agent API")

# Allow CORS for tablet and dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from typing import Optional

class QueryRequest(BaseModel):
    query: str
    device_id: str = "tablet-001"
    lat: Optional[float] = None
    lon: Optional[float] = None
    store_id: Optional[str] = None

class DeviceStatus(BaseModel):
    device_id: str
    status: str
    battery_level: int

@app.on_event("startup")
def startup_event():
    # Initialize the mock inventory database on startup
    init_db()

@app.post("/api/chat")
def chat_endpoint(request: QueryRequest):
    """Tablet endpoint. Handles voice/text queries."""
    # Update device last seen
    update_device_status(request.device_id, "online", 100)
    
    try:
        # Pass the device_id as the session_id to maintain conversational state
        response = handle_user_query(
            request.query,
            session_id=request.device_id,
            user_lat=request.lat,
            user_lon=request.lon,
            user_store_id=request.store_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/devices/heartbeat")
def heartbeat(status: DeviceStatus):
    """Tablet endpoint. Reports device health."""
    update_device_status(status.device_id, status.status, status.battery_level)
    return {"status": "recorded"}

@app.get("/api/analytics/searches")
def get_recent_searches():
    """Dashboard endpoint. Get recent queries and intent metrics."""
    conn = sqlite3.connect(ANALYTICS_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM search_logs ORDER BY timestamp DESC LIMIT 50")
    logs = [dict(row) for row in cursor.fetchall()]
    
    # Simple aggregate metrics
    cursor.execute("SELECT COUNT(*) FROM search_logs WHERE redirected_to_competitor = 1")
    lost_sales_count = cursor.fetchone()[0]
    
    conn.close()
    return {
        "recent_logs": logs,
        "lost_sales": lost_sales_count
    }

@app.get("/api/analytics/devices")
def get_devices():
    """Dashboard endpoint. Get tablet fleet health."""
    conn = sqlite3.connect(ANALYTICS_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM devices")
    devices = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return {"devices": devices}
