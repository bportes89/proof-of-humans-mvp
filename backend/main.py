from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import time

# Add root directory to path to import pipeline
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pipeline.manager import pipeline

app = FastAPI(title="Proof of Humans API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve client
app.mount("/static", StaticFiles(directory="client"), name="static")

class EnrollRequest(BaseModel):
    user_id: str

class VerifyRequest(BaseModel):
    user_id: str

@app.on_event("startup")
def startup_event():
    pipeline.start()

@app.on_event("shutdown")
def shutdown_event():
    pipeline.stop()

@app.get("/")
def read_root():
    return FileResponse("client/index.html")

@app.post("/enroll")
def enroll(request: EnrollRequest):
    session_id = pipeline.start_session(request.user_id, mode="ENROLL")
    return {"session_id": session_id, "message": "Enrollment session started. Please face the camera and breathe naturally."}

@app.post("/verify")
def verify(request: VerifyRequest):
    session_id = pipeline.start_session(request.user_id, mode="VERIFY")
    return {"session_id": session_id, "message": "Verification session started. Please face the camera and breathe deep."}

@app.get("/status")
def get_status():
    return pipeline.get_status()

@app.get("/frame")
def get_frame():
    # Returns a single frame as base64 JSON
    b64_frame = pipeline.get_latest_frame_b64()
    if b64_frame is None:
        return {"frame": None}
    return {"frame": b64_frame}

@app.get("/proof/{session_id}")
def get_proof(session_id: str):
    status = pipeline.get_status()
    # In a real DB we would store proofs. Here we just return if it matches current session or memory.
    # For MVP, we only keep the current/last proof in memory.
    
    if status["session_id"] == session_id:
        if status["proof"]:
            return status["proof"]
        else:
            raise HTTPException(status_code=404, detail="Proof not ready yet")
    
    # If session mismatch, we might have lost it (MVP limitation)
    raise HTTPException(status_code=404, detail="Session not found or expired")

# Simple MJPEG stream endpoint for easier consumption by <img> tag
@app.get("/video_feed")
def video_feed():
    def iterfile():
        while True:
            b64_str = pipeline.get_latest_frame_b64()
            if b64_str:
                import base64
                img_data = base64.b64decode(b64_str)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + img_data + b'\r\n')
            else:
                pass
            time.sleep(0.05)
            
    return StreamingResponse(iterfile(), media_type="multipart/x-mixed-replace;boundary=frame")
