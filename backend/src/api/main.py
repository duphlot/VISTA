import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
import asyncio
from pathlib import Path
import cv2
import torch
import clip
from dotenv import load_dotenv

# Import your existing modules
from workflow.main import process_video
from src.utils.basetools.preprocess_video import VideoPreprocessor
from src.utils.agents.image_relation_agent import ImageRelationAgent, ImageRelationInput, RelationOutput
from src.utils.agents.scene_graph_agent import SameEntityAgent, SceneGraphInput
from src.utils.agents.graph_reasoning_agent import GraphReasoningAgent, GraphReasoningInput

load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="soICT Video Analysis API", version="0.1.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables to store models and sessions
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
sessions: Dict[str, Dict[str, Any]] = {}

# Mount static files for serving uploaded videos and results
app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.mount("/results", StaticFiles(directory="output"), name="results")

# Pydantic models
class VideoAnalysisRequest(BaseModel):
    question: str
    session_id: Optional[str] = None

class VideoAnalysisResponse(BaseModel):
    session_id: str
    answer: str
    keyframes_count: int
    output_dir: str
    relations: Dict[str, List[str]]
    scene_graph: List[str]

class ChatMessage(BaseModel):
    content: str
    role: str  # "user" or "assistant"
    id: str
    parts: Optional[List[Dict[str, Any]]] = None

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class SessionInfo(BaseModel):
    session_id: str
    video_path: Optional[str] = None
    status: str
    created_at: str

@app.get("/")
async def root():
    return {"message": "soICT Video Analysis API", "version": "0.1.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "device": device}

@app.post("/api/sessions", response_model=SessionInfo)
async def create_session():
    """Create a new session"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "id": session_id,
        "video_path": None,
        "status": "created",
        "created_at": str(asyncio.get_event_loop().time()),
        "messages": [],
        "last_result": None
    }
    
    return SessionInfo(
        session_id=session_id,
        status="created",
        created_at=sessions[session_id]["created_at"]
    )

@app.get("/api/sessions/{session_id}", response_model=SessionInfo)
async def get_session(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return SessionInfo(
        session_id=session_id,
        video_path=session.get("video_path"),
        status=session["status"],
        created_at=session["created_at"]
    )

@app.post("/api/sessions/{session_id}/upload")
async def upload_video(session_id: str, file: UploadFile = File(...)):
    """Upload video file to session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Create upload directory
    upload_dir = Path("uploads/videos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Save uploaded file
    video_path = upload_dir / f"{session_id}_{file.filename}"
    
    try:
        content = await file.read()
        with open(video_path, "wb") as f:
            f.write(content)
        
        # Update session
        sessions[session_id]["video_path"] = str(video_path)
        sessions[session_id]["status"] = "video_uploaded"
        
        return {
            "message": f"Video uploaded successfully: {file.filename}",
            "video_path": str(video_path),
            "session_id": session_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading video: {str(e)}")

@app.post("/api/sessions/{session_id}/analyze", response_model=VideoAnalysisResponse)
async def analyze_video(session_id: str, request: VideoAnalysisRequest):
    """Analyze video with question"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    video_path = session.get("video_path")
    
    if not video_path or not Path(video_path).exists():
        raise HTTPException(status_code=400, detail="No video uploaded for this session")
    
    try:
        # Update session status
        sessions[session_id]["status"] = "processing"
        
        # Process video using existing function
        result = process_video(video_path, request.question)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to process video")
        
        # Update session with result
        sessions[session_id]["last_result"] = result
        sessions[session_id]["status"] = "completed"
        
        # Add to messages
        user_message = {
            "content": request.question,
            "role": "user",
            "id": str(uuid.uuid4())
        }
        
        assistant_message = {
            "content": result["answer"],
            "role": "assistant", 
            "id": str(uuid.uuid4()),
            "parts": [
                {"type": "text", "content": result["answer"], "author": "Video Analyst"}
            ]
        }
        
        sessions[session_id]["messages"].extend([user_message, assistant_message])
        
        return VideoAnalysisResponse(
            session_id=session_id,
            answer=result["answer"],
            keyframes_count=len(result["keyframes"]),
            output_dir=str(result["output_dir"]),
            relations=result["relations"],
            scene_graph=result["scene_graph"]
        )
        
    except Exception as e:
        sessions[session_id]["status"] = "error"
        raise HTTPException(status_code=500, detail=f"Error analyzing video: {str(e)}")

@app.get("/api/sessions/{session_id}/messages")
async def get_messages(session_id: str):
    """Get chat messages for session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"messages": sessions[session_id].get("messages", [])}

@app.post("/api/sessions/{session_id}/chat")
async def chat_with_video(session_id: str, request: ChatRequest):
    """Chat about the analyzed video"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    last_result = session.get("last_result")
    
    if not last_result:
        raise HTTPException(status_code=400, detail="No video analysis found. Please analyze a video first.")
    
    try:
        # Use the existing scene graph for reasoning
        graph_text = "\n".join(last_result["scene_graph"])
        
        reasoning_agent = GraphReasoningAgent()
        input_data = GraphReasoningInput(
            question=request.message,
            graph_text=graph_text
        )
        
        result = reasoning_agent.run(input_data)
        answer = result.answer
        
        # Add messages to session
        user_message = {
            "content": request.message,
            "role": "user",
            "id": str(uuid.uuid4())
        }
        
        assistant_message = {
            "content": answer,
            "role": "assistant",
            "id": str(uuid.uuid4()),
            "parts": [
                {"type": "text", "content": answer, "author": "Video Analyst"}
            ]
        }
        
        sessions[session_id]["messages"].extend([user_message, assistant_message])
        
        return assistant_message
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and its associated files"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session = sessions[session_id]
        
        # Clean up video file if exists
        video_path = session.get("video_path")
        if video_path and Path(video_path).exists():
            Path(video_path).unlink()
        
        # Remove session
        del sessions[session_id]
        
        return {"message": "Session deleted successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "status": data["status"],
                "created_at": data["created_at"],
                "has_video": data.get("video_path") is not None
            }
            for sid, data in sessions.items()
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)