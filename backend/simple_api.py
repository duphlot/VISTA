import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import json
import uuid
import asyncio
from pathlib import Path
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(title="soICT Video Analysis API", version="0.1.0")

# CORS middleware for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", 
        "http://localhost:3000", 
        "http://localhost:8501",  # Vite dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:8501",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept", 
        "Accept-Language", 
        "Content-Language", 
        "Content-Type",
        "Authorization",
        "X-Requested-With"
    ],
)

# Global variables to store sessions
sessions: Dict[str, Dict[str, Any]] = {}

# Create directories
Path("uploads").mkdir(exist_ok=True)
Path("output").mkdir(exist_ok=True)

# Async video processing function
async def process_video_async(session_id: str, video_path: Path):
    """Process video asynchronously"""
    try:
        print(f"🎯 [PROCESSING] Starting video analysis for session: {session_id}")
        print(f"🎬 [PROCESSING] Video path: {video_path}")
        
        # Update session status
        sessions[session_id]["status"] = "processing"
        
        # Simulate processing time (in real app, this would be actual video analysis)
        print(f"⏳ [PROCESSING] Extracting keyframes...")
        await asyncio.sleep(2)  # Simulate keyframe extraction
        
        print(f"🔍 [PROCESSING] Analyzing video content...")
        await asyncio.sleep(3)  # Simulate video analysis
        
        print(f"🏗️ [PROCESSING] Building scene graph...")
        await asyncio.sleep(2)  # Simulate scene graph generation
        
        # Create output directory
        output_dir = Path("output") / "keyframes_output" / session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 [PROCESSING] Created output directory: {output_dir}")
        
        # Mock results (replace with real video analysis)
        result = {
            "session_id": session_id,
            "answer": f"✅ Video analysis completed! Analyzed video: {video_path.name}",
            "keyframes_count": 15,
            "output_dir": str(output_dir),
            "relations": {
                "frame_0": ["person -> walking", "car -> parked"],
                "frame_5": ["person -> crossing", "traffic_light -> red"],
                "frame_10": ["person -> arrived", "building -> entrance"]
            },
            "scene_graph": ["person walks to building", "car remains stationary", "traffic light changes color"]
        }
        
        # Update session with result
        sessions[session_id]["last_result"] = result
        sessions[session_id]["status"] = "completed"
        
        print(f"✅ [PROCESSING] Video analysis completed for session: {session_id}")
        print(f"📊 [RESULTS] Found {result['keyframes_count']} keyframes")
        print(f"🔗 [RESULTS] Generated {len(result['scene_graph'])} scene graph relations")
        
    except Exception as e:
        print(f"❌ [ERROR] Processing failed for session {session_id}: {str(e)}")
        sessions[session_id]["status"] = "processing_error"
        sessions[session_id]["error"] = str(e)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="uploads"), name="static")
    app.mount("/results", StaticFiles(directory="output"), name="results")
except Exception as e:
    print(f"Warning: Could not mount static files: {e}")

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
    role: str
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

class ChatResponse(BaseModel):
    message: str
    session_id: str

@app.get("/")
async def root():
    return {"message": "soICT Video Analysis API", "version": "0.1.0", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

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

@app.get("/api/sessions/{session_id}/status")
async def get_processing_status(session_id: str):
    """Get processing status for session"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    
    # Format analysis results if available
    analysis_results = None
    if session.get("last_result"):
        result = session["last_result"]
        analysis_results = {
            "keyframes_count": result.get("keyframes_count", 0),
            "scene_graph_relations": len(result.get("scene_graph", [])),
            "video_duration": result.get("video_duration")
        }
    
    status_info = {
        "session_id": session_id,
        "status": session["status"],
        "video_path": session.get("video_path"),
        "filename": session.get("filename"),
        "analysis_results": analysis_results,
        "created_at": session.get("created_at", ""),
        "error": session.get("error")
    }
    
    print(f"📊 [STATUS] Session {session_id}: {session['status']}")
    return status_info

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
    print(f"🎬 [UPLOAD] Starting video upload for session: {session_id}")
    print(f"📁 [UPLOAD] File: {file.filename}, Content-Type: {file.content_type}, Size: {file.size}")
    
    if session_id not in sessions:
        print(f"❌ [ERROR] Session {session_id} not found")
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not file.content_type or not file.content_type.startswith("video/"):
        print(f"❌ [ERROR] Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Create upload directory
    upload_dir = Path("uploads/videos")
    upload_dir.mkdir(parents=True, exist_ok=True)
    print(f"📂 [UPLOAD] Created upload directory: {upload_dir}")
    
    # Save uploaded file
    video_path = upload_dir / f"{session_id}_{file.filename}"
    
    try:
        print(f"💾 [UPLOAD] Saving video to: {video_path}")
        content = await file.read()
        file_size_mb = len(content) / (1024 * 1024)
        print(f"📊 [UPLOAD] Video file size: {file_size_mb:.2f} MB")
        
        with open(video_path, "wb") as f:
            f.write(content)
        
        print(f"✅ [UPLOAD] Video saved successfully!")
        
        # Update session
        sessions[session_id]["video_path"] = str(video_path)
        sessions[session_id]["status"] = "video_uploaded"
        sessions[session_id]["filename"] = file.filename
        
        print(f"🔄 [SESSION] Updated session {session_id} status to 'video_uploaded'")
        
        # Automatically start video processing
        print(f"🚀 [PROCESSING] Starting automatic video analysis...")
        await process_video_async(session_id, video_path)
        
        return {
            "message": f"Video uploaded and processing started: {file.filename}",
            "video_path": str(video_path),
            "session_id": session_id,
            "status": "processing"
        }
        
    except Exception as e:
        print(f"❌ [ERROR] Upload failed: {str(e)}")
        sessions[session_id]["status"] = "upload_error" 
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
        
        # Mock processing for now - replace with actual video processing
        answer = f"Đã phân tích video thành công! Câu hỏi: '{request.question}'. Video path: {video_path}"
        
        # Mock result
        result = {
            "session_id": session_id,
            "answer": answer,
            "keyframes_count": 10,
            "output_dir": f"output/keyframes_output/{session_id}",
            "relations": {"frame_0": ["object1 -> object2"], "frame_1": ["object2 -> object3"]},
            "scene_graph": ["relation1", "relation2", "relation3"]
        }
        
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
            "content": answer,
            "role": "assistant", 
            "id": str(uuid.uuid4()),
            "parts": [
                {"type": "text", "content": answer, "author": "Video Analyst"}
            ]
        }
        
        sessions[session_id]["messages"].extend([user_message, assistant_message])
        
        return VideoAnalysisResponse(**result)
        
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
async def chat_with_video(session_id: str, request: dict):
    """Chat about the analyzed video using real agents"""
    print(f"🔄 [CHAT] Processing chat for session: {session_id}")
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video analysis not completed yet")
    
    question = request.get("message", "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="Message is required")
    
    print(f"💬 [CHAT] Session {session_id}: {question}")
    
    try:
        # Get the video path and session data
        video_path = session.get("video_path")
        if not video_path or not Path(video_path).exists():
            print(f"❌ [CHAT] Video file not found: {video_path}")
            raise HTTPException(status_code=400, detail="Video file not found")
        
        print(f"🔄 [CHAT] Using real agents to process question...")
        print(f"� [CHAT] Video path: {video_path}")
        
        # Import the process_video function from workflow  
        try:
            # Add parent directory to path to import workflow
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            print(f"🔧 [CHAT] Import path added: {parent_dir}")
            from workflow.main import process_video
            print(f"✅ [CHAT] Successfully imported process_video")
            
        except ImportError as import_error:
            print(f"❌ [CHAT] Import error: {import_error}")
            print(f"📂 [CHAT] Current directory: {os.getcwd()}")
            print(f"🐍 [CHAT] Python path: {sys.path}")
            raise HTTPException(status_code=500, detail=f"Import error: {str(import_error)}")
        
        print(f"🤖 [CHAT] Calling process_video with question: {question}")
        try:
            result = process_video(video_path, question)
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                print(f"❌ [CHAT] API unavailable: {str(e)}")
                return ChatResponse(
                    message="Xin lỗi, hệ thống AI tạm thời quá tải. Vui lòng thử lại sau 2-3 phút.",
                    session_id=session_id
                )
            else:
                print(f"❌ [CHAT] Processing error: {str(e)}")
                raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
                
        print(f"📊 [CHAT] Process result type: {type(result)}")
        
        if not result:
            print(f"❌ [CHAT] process_video returned None")
            raise HTTPException(status_code=500, detail="Failed to process video with agents")
        
        answer = result.get("answer", "Không thể tạo câu trả lời.")
        print(f"🤖 [CHAT] Agent response: {answer[:200]}...")
        
        # Store chat history in session
        if "chat_history" not in session:
            session["chat_history"] = []
        
        chat_entry = {
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        session["chat_history"].append(chat_entry)
        
        return {
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        print(f"❌ [CHAT] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat processing error: {str(e)}")

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
    uvicorn.run(app, host="0.0.0.0", port=8000)