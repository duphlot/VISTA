import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import time
from dotenv import load_dotenv
import chainlit as cl
from pathlib import Path
import cv2
import torch
import clip
from pathlib import Path
from src.utils.agents.captain_agent import CaptainAgent

load_dotenv()
device = "cuda" if torch.cuda.is_available() else "cpu"
clip_model, clip_preprocess = clip.load("ViT-B/32", device=device)
print(f"CLIP model loaded on {device}")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

BATCH_SIZE = 8
HIDDEN_DIM = 512
NUM_HEADS = 8

def process_video(video_path: str, question: str = "Mô tả nội dung của video này"):
    """
    Process video using the VISTA Multi-Agent framework
    
    Args:
        video_path: Path to the video file
        question: Question to ask about the video
    """
    sample_video_path = Path(video_path)
    
    if not sample_video_path.exists():
        print(f"Video not found at: {sample_video_path}")
        return None
    
    # Create output directory in the project folder
    output_dir = Path(f"./output/keyframes_output/{sample_video_path.stem}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize VISTA Captain Agent
    captain = CaptainAgent()
    
    # Run the VISTA orchestration pipeline
    result = captain.process_video(str(sample_video_path), question)
    
    # Save keyframes for frontend UI display
    for i, frame in enumerate(result["keyframes"]):
        frame_path = output_dir / f"frame_{i:04d}.jpg"
        cv2.imwrite(str(frame_path), cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        
    print(f"Saved keyframes to {output_dir}")
    
    # Merge output_dir into results
    result["output_dir"] = output_dir
    
    return result

@cl.on_chat_start
async def start():
    await cl.Message(
        content="Xin chào! Hãy upload video của bạn để tôi phân tích."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # Check if there are any files attached
    if message.elements:
        video_file = None
        for element in message.elements:
            if element.mime and element.mime.startswith("video/"):
                video_file = element
                break
        
        if video_file:
            # Debug information
            print(f"Video file type: {type(video_file)}")
            print(f"Video file attributes: {dir(video_file)}")
            print(f"Video file name: {video_file.name}")
            if hasattr(video_file, 'content'):
                print(f"Content type: {type(video_file.content)}")
                print(f"Content is None: {video_file.content is None}")
            
            # Save uploaded video to local directory
            video_dir = Path("./uploads/videos")
            video_dir.mkdir(parents=True, exist_ok=True)
            
            video_path = video_dir / video_file.name
            
            try:
                # Try different methods to get file content
                content = None
                
                # Method 1: Direct content access
                if hasattr(video_file, 'content') and video_file.content is not None:
                    content = video_file.content
                    print("Using direct content access")
                
                # Method 2: Path-based reading
                elif hasattr(video_file, 'path') and video_file.path:
                    print(f"Using path-based reading: {video_file.path}")
                    with open(video_file.path, "rb") as src:
                        content = src.read()
                
                # Method 3: Async content reading (for newer Chainlit versions)
                elif hasattr(video_file, 'read'):
                    print("Using async read method")
                    content = await video_file.read()
                
                if content is None:
                    await cl.Message(content="Lỗi: Không thể đọc nội dung file video. Vui lòng thử lại.").send()
                    return
                
                # Write content to file
                with open(video_path, "wb") as f:
                    f.write(content)
                    
            except Exception as e:
                print(f"Error handling file: {e}")
                await cl.Message(content=f"Lỗi khi xử lý file: {str(e)}").send()
                return
            
            await cl.Message(content=f"Đã nhận video: {video_file.name}. Đang xử lý...").send()
            
            # Get question from message text
            question = message.content if message.content.strip() else "Mô tả nội dung của video này"
            
            try:
                # Process video
                result = process_video(str(video_path), question)
                
                if result:
                    response = f"**Câu hỏi:** {question}\n\n"
                    response += f"**Trả lời:** {result['answer']}\n\n"
                    response += f"**Số khung hình được phân tích:** {len(result['keyframes'])}\n"
                    response += f"**Keyframes đã lưu tại:** {result['output_dir']}"
                    
                    await cl.Message(content=response).send()
                else:
                    await cl.Message(content="Không thể xử lý video. Vui lòng kiểm tra định dạng file.").send()
                    
            except Exception as e:
                await cl.Message(content=f"Lỗi khi xử lý video: {str(e)}").send()
        else:
            await cl.Message(content="Vui lòng upload file video.").send()
    else:
        await cl.Message(content="Vui lòng upload video để tôi có thể phân tích.").send()

# For running directly (not through Chainlit)
if __name__ == "__main__":
    # Example usage
    video_path = input("Nhập đường dẫn đến video: ")
    question = input("Nhập câu hỏi (hoặc Enter để dùng mặc định): ") or "Mô tả nội dung của video này"
    
    result = process_video(video_path, question)