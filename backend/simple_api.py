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
app = FastAPI(title="VISTA Video Analysis API", version="0.1.0")

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
    """Process video asynchronously using real workflow"""
    try:
        print(f"🎯 [PROCESSING] Starting REAL video analysis for session: {session_id}")
        print(f"🎬 [PROCESSING] Video path: {video_path}")
        
        # Update session status
        sessions[session_id]["status"] = "processing"
        
        # Import the real workflow
        try:
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            print(f"🔧 [PROCESSING] Import path added: {parent_dir}")
            from workflow.main import process_video
            print(f"✅ [PROCESSING] Successfully imported process_video")
            
        except ImportError as import_error:
            print(f"❌ [PROCESSING] Import error: {import_error}")
            raise Exception(f"Cannot import workflow: {import_error}")
        
        print(f"⏳ [PROCESSING] Running real video analysis...")
        
        # Call the real process_video function
        # Using a default question for automatic processing
        default_question = "Hãy mô tả nội dung chính của video này."
        
        try:
            result_data = process_video(str(video_path), default_question)
            print(f"📊 [PROCESSING] Real workflow completed!")
            print(f"🎯 [PROCESSING] Result keys: {list(result_data.keys()) if result_data else 'None'}")
            
            # Debug: Print all result data to understand structure
            if result_data:
                print(f"🔍 [DEBUG] Full result_data: {result_data}")
            
        except Exception as process_error:
            print(f"❌ [PROCESSING] Real processing failed: {process_error}")
            # Fallback to basic processing info
            result_data = {
                "answer": f"Đã upload và xử lý video: {video_path.name}. Lỗi xử lý: {str(process_error)}",
                "keyframes_count": 0,
                "scene_graph": [],
                "video_info": {}
            }
        
        # Create output directory
        output_dir = Path("output") / "keyframes_output" / session_id
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 [PROCESSING] Created output directory: {output_dir}")
        
        # Extract real video information for UI
        video_info = result_data.get("video_info", {})
        
        # Try different ways to get keyframes count
        keyframes_count = 0
        if "keyframes_count" in result_data:
            keyframes_count = result_data["keyframes_count"]
        elif "keyframes" in result_data:
            keyframes_count = len(result_data["keyframes"]) if isinstance(result_data["keyframes"], list) else result_data["keyframes"]
        elif "selected_keyframes" in result_data:
            keyframes_count = result_data["selected_keyframes"]
        
        print(f"🔍 [DEBUG] Extracted keyframes_count: {keyframes_count}")
        
        # Create detailed analysis summary
        analysis_summary = f"📹 Video Analysis Results:\n"
        if video_info:
            analysis_summary += f"• Duration: {video_info.get('duration', 'Unknown')} seconds\n"
            analysis_summary += f"• Resolution: {video_info.get('width', '?')}x{video_info.get('height', '?')}\n"
            analysis_summary += f"• FPS: {video_info.get('fps', 'Unknown')}\n"
            analysis_summary += f"• Total frames: {video_info.get('frame_count', 'Unknown')}\n"
        analysis_summary += f"• Keyframes selected: {keyframes_count}\n"
        
        # Format the real results
        result = {
            "session_id": session_id,
            "answer": result_data.get("answer", analysis_summary),
            "keyframes_count": keyframes_count,
            "output_dir": str(output_dir),
            "relations": result_data.get("relations", {}),
            "scene_graph": result_data.get("scene_graph", []),
            "video_info": video_info  # Include video metadata
        }
        
        # Update session with result
        sessions[session_id]["last_result"] = result
        sessions[session_id]["status"] = "completed"
        sessions[session_id]["scene_graph"] = result_data.get("scene_graph", [])
        sessions[session_id]["analysis_data"] = result_data  # Store full analysis for reuse
        
        print(f"✅ [PROCESSING] REAL video analysis completed for session: {session_id}")
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
    return {"message": "VISTA Video Analysis API", "version": "0.1.0", "status": "running"}

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
    print(f"📊 [STATUS] Checking status for session: {session_id}")
    print(f"📋 [STATUS] Available sessions: {list(sessions.keys())}")
    
    if session_id not in sessions:
        print(f"❌ [STATUS] Session {session_id} not found in memory")
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    print(f"📊 [STATUS] Session data: {session}")
    
    # Format analysis results if available
    analysis_results = None
    if session.get("last_result"):
        result = session["last_result"]
        video_info = result.get("video_info", {})
        
        analysis_results = {
            "keyframes_count": result.get("keyframes_count", 0),
            "scene_graph_relations": len(result.get("scene_graph", [])),
            "video_duration": video_info.get("duration"),
            "video_resolution": f"{video_info.get('width', '?')}x{video_info.get('height', '?')}" if video_info.get('width') else None,
            "video_fps": video_info.get("fps"),
            "video_frame_count": video_info.get("frame_count")
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
    
    print(f"📊 [STATUS] Returning status: {status_info}")
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
    print(f"📋 [UPLOAD] Total sessions before upload: {len(sessions)}")
    
    if session_id not in sessions:
        print(f"❌ [ERROR] Session {session_id} not found in memory")
        print(f"📋 [ERROR] Available sessions: {list(sessions.keys())}")
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
        print(f"📋 [SESSION] Session data: {sessions[session_id]}")
        
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
    """Chat about the analyzed video using pre-computed scene graph"""
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
        # Use pre-computed analysis data instead of reprocessing
        analysis_data = session.get("analysis_data", {})
        scene_graph = session.get("scene_graph", [])
        
        if not analysis_data or not scene_graph:
            print(f"❌ [CHAT] No pre-computed analysis data found")
            raise HTTPException(status_code=400, detail="No scene graph data available")
        
        print(f"🔄 [CHAT] Using pre-computed scene graph with {len(scene_graph)} relations")
        print(f"📊 [CHAT] Analysis data keys: {list(analysis_data.keys())}")
        
        # Import and use GraphReasoningAgent
        try:
            parent_dir = os.path.dirname(os.path.dirname(__file__))
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
            
            print(f"🔧 [CHAT] Import path added: {parent_dir}")
            
            # Import GraphReasoningAgent for intelligent chat
            from src.utils.agents.graph_reasoning_agent import GraphReasoningAgent, GraphReasoningInput
            print(f"✅ [CHAT] Successfully imported GraphReasoningAgent")
            
            # Convert scene graph to text format
            graph_text = "\n".join(scene_graph) if isinstance(scene_graph, list) else str(scene_graph)
            
            # Use GraphReasoningAgent to answer question based on scene graph
            reasoning_agent = GraphReasoningAgent()
            reasoning_input = GraphReasoningInput(
                question=question,
                graph_text=graph_text,
                top_k=200
            )
            
            print(f"🤖 [CHAT] Using GraphReasoningAgent with {len(scene_graph)} scene graph items")
            result = reasoning_agent.run(reasoning_input)
            answer = result.answer
            print(f"🤖 [CHAT] Agent response: {answer[:200]}...")
            
        except ImportError as e:
            print(f"❌ [CHAT] Could not import GraphReasoningAgent: {e}")
            # Basic fallback if agent import fails
            answer = f"Xin lỗi, không thể tải agent. Dựa trên scene graph có {len(scene_graph)} mối quan hệ, tôi không thể trả lời chi tiết cho câu hỏi: '{question}'"
            
        except Exception as e:
            print(f"❌ [CHAT] GraphReasoningAgent error: {e}")
            # Fallback for agent execution errors
            if "503" in str(e) or "UNAVAILABLE" in str(e) or "quá tải" in str(e):
                answer = "Xin lỗi, hệ thống AI tạm thời quá tải. Vui lòng thử lại sau 2-3 phút."
            else:
                answer = f"Có lỗi khi xử lý câu hỏi: {str(e)}"
        
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
    print(f"📋 [DEBUG] Total sessions in memory: {len(sessions)}")
    for sid, data in sessions.items():
        print(f"  📁 Session {sid}: status={data['status']}, video={data.get('filename', 'none')}")
    
    return {
        "sessions": [
            {
                "session_id": sid,
                "status": data["status"],
                "created_at": data["created_at"],
                "has_video": data.get("video_path") is not None,
                "filename": data.get("filename")
            }
            for sid, data in sessions.items()
        ]
    }

@app.delete("/api/sessions")
async def clear_all_sessions():
    """Clear all sessions from memory"""
    global sessions
    count = len(sessions)
    sessions = {}
    print(f"🧹 [CLEAR] Cleared {count} sessions from memory")
    return {"message": f"Cleared {count} sessions", "sessions_cleared": count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)