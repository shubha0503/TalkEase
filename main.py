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
HEADERS = {"Authorization": "Bearer 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"}  

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




#OLD CODE WITH THE CHAT DEFINED HERE ONLYY

# Store chat history per WebSocket session
# chat_sessions = {}

# def chat(prompt: str, session_id=None):
#     """Sends a dynamic request to Mixtral API for varied responses with session context."""
    
#     # Keep chat history if session exists
#     if session_id and session_id in chat_sessions:
#         chat_sessions[session_id].append(f"User: {prompt}")
#         conversation_history = "\n".join(chat_sessions[session_id][-5:])  # Keep last 5 messages
#         formatted_prompt = f"<s> [INST] Continue this conversation naturally:\n{conversation_history} [/INST]"
#     else:
#         formatted_prompt = f"<s> [INST] {prompt} Provide a varied and engaging response. Avoid repetition. [/INST]"

#     payload = {
#         "inputs": formatted_prompt,
#         "parameters": {"max_length": 150, "temperature": 0.8, "top_p": 0.9}
#     }

#     try:
#         response = requests.post(API_URL, headers=HEADERS, json=payload)
#         response.raise_for_status()
#         result = response.json()
        
#         bot_response = result[0]["generated_text"] if isinstance(result, list) else "Error: Unexpected response format"

#         if session_id:
#             chat_sessions[session_id].append(f"Bot: {bot_response}")

#         return bot_response
#     except requests.exceptions.RequestException as e:
#         return f"API Error: {str(e)}"

# @app.get("/chat/")
# def chat_with_ai(prompt: str):
#     """Endpoint for AI chat."""
#     return {"response": chat(prompt)}

# class LessonRequest(BaseModel):
#     topic: str
#     language: str

# @app.post("/generate_lesson/")
# async def generator(request: LessonRequest):
#     """API Endpoint to generate a lesson."""
#     lesson = generate_lesson(request.topic, request.language)
    
#     if "API Error" in lesson:
#         raise HTTPException(status_code=500, detail=lesson)
    
#     return {"topic": request.topic, "language": request.language, "lesson": lesson}

# @app.websocket("/ws/chat")
# async def websocket_chat(websocket: WebSocket):
#     """WebSocket endpoint for real-time chat with session history."""
#     await websocket.accept()
    
#     session_id = id(websocket)  # Unique session ID for each connection
#     chat_sessions[session_id] = []  # Store conversation history
    
#     while True:
#         prompt = await websocket.receive_text()
#         response = chat(prompt, session_id)
#         await websocket.send_text(response)

# @app.get("/")
# def root():
#     return {"message": "Welcome to the Language Learning API! How can I help you today?"}