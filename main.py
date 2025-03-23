import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from pydantic import BaseModel
from ChatBot import chat, chat_sessions  
from Lesson_Generator import generate_lesson 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify domains instead of "*" for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer Your API Key"}  

class LessonRequest(BaseModel):
    topic: str
    language: str

@app.get("/chat/")
def chat_with_ai(prompt: str):
    """Endpoint for AI chat."""
    return {"response": chat(prompt)}

@app.post("/generate_lesson/")
async def generator(request: LessonRequest):
    """API Endpoint to generate a lesson."""
    lesson = generate_lesson(request.topic, request.language)
    
    if "API Error" in lesson:
        raise HTTPException(status_code=500, detail=lesson)
    
    return {"topic": request.topic, "language": request.language, "lesson": lesson}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket endpoint for real-time chat with session history."""
    await websocket.accept()
    
    session_id = id(websocket)  # Generate a unique session ID

    # ✅ Ensure session is initialized before usage
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []  

    try:
        while True:
            prompt = await websocket.receive_text()
            response = chat(prompt, session_id)  # This calls the imported chat function
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print(f"WebSocket {session_id} disconnected.")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        # ✅ Clean up the session when WebSocket disconnects
        chat_sessions.pop(session_id, None)


@app.get("/")
def root():
    return {"message": "Welcome to the Language Learning API! How can I help you today?"}
