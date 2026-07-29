import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any

from gateway import MicroHAGateway

# Logging configuration
logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger(__name__)

# Initialize FastAPI and our gateway
app = FastAPI(title="MicroHA Gateway API", description="Gateway for ESP32/ESP8266 to Home Assistant")

# HA Access Configuration
HA_URL = "http://homeassistant.local:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI0YTNkMTkxODRlNGU0NGY3YTcxZGI0ZTcwZWNlYTFlYyIsImlhdCI6MTc4NTMyNTY1MywiZXhwIjoyMTAwNjg1NjUzfQ.Ec-WuE3DBWxtQlkW1JIMMlRTcjXxKAG4aF5ii_krqJ4"
gateway = MicroHAGateway(ha_url=HA_URL, token=TOKEN)

class CommandRequest(BaseModel):
    entity_id: str
    action: str
    params: Optional[Dict[str, Any]] = None

@app.get("/api/devices")
def get_devices():
    """Get all grouped devices in a compact format."""
    try:
        groups = gateway.get_grouped_devices()
        return groups
    except Exception as e:
        _LOGGER.error(f"Error fetching devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/command")
def send_command(req: CommandRequest):
    """Send a command (e.g., toggle) to a specific device."""
    _LOGGER.info(f"Received command {req.action} for {req.entity_id}")
    
    result = gateway.control_device(
        entity_id=req.entity_id,
        action=req.action,
        params=req.params,
        dry_run=False # Set to False for production
    )
    
    if result.get("status") == "error":
        raise HTTPException(status_code=500, detail=result.get("message"))
        
    return result
