import uvicorn
import logging

if __name__ == "__main__":
    print("=" * 65)
    print("      MICRO-HA GATEWAY FASTAPI SERVER IS STARTING...      ")
    print("=" * 65)
    
    # Run the FastAPI app from server.py
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True, log_level="info")
