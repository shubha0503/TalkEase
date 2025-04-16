import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect, Depends
from pydantic import BaseModel
from ChatBot import chat, chat_sessions  
from Lesson_Generator import generate_lesson 
import firebase_admin
from firebase_admin import credentials, firestore
import httpx
import os
from google.cloud import firestore
from Quiz import generate_quiz
from Quiz import fetch_latest_lesson

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/hp/Downloads/talkease-d404e-firebase-adminsdk-fbsvc-cc6f68df96.json"

cred = credentials.Certificate("C:/Users/hp/Downloads/talkease-d404e-firebase-adminsdk-fbsvc-cc6f68df96.json")
firebase_admin.initialize_app(cred)
db = firestore.Client()  # Firestore Database

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can specify domains instead of "*" for security
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer YOUR HF KEY"}  

class LessonRequest(BaseModel):
    topic: str
    language: str

@app.get("/chat/")
def chat_with_ai(prompt: str):
    """Endpoint for AI chat."""
    return {"response": chat(prompt)}

from google.cloud import firestore

db = firestore.Client()  # Firestore Client Initialize

async def store_lesson_in_firestore(topic: str, language: str, lesson: str):
    lesson_data = {
        "topic": topic,
        "language": language,
        "lesson": lesson,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("lessons").add(lesson_data)

@app.post("/generate_lesson/")
async def generator(request: LessonRequest):
    """API Endpoint to generate and store a lesson."""
    lesson = generate_lesson(request.topic, request.language)
    
    if "API Error" in lesson:
        raise HTTPException(status_code=500, detail=lesson)
    
    await store_lesson_in_firestore(request.topic, request.language, lesson)  # Store in Firestore
    return {"topic": request.topic, "language": request.language, "lesson": lesson}

async def store_chat_message(session_id: str, user_input: str, ai_response: str):
    chat_data = {
        "session_id": session_id,
        "user_input": user_input,
        "ai_response": ai_response,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("chats").add(chat_data)  # Store in Firestore

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """WebSocket for real-time AI chat, now with Firestore storage."""
    await websocket.accept()
    
    session_id = str(id(websocket))  # Unique session ID

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    try:
        while True:
            prompt = await websocket.receive_text()
            response = chat(prompt, session_id)  
            await websocket.send_text(response)

            await store_chat_message(session_id, prompt, response)  # Store in Firestore
    except WebSocketDisconnect:
        print(f"WebSocket {session_id} disconnected.")
    finally:
        chat_sessions.pop(session_id, None)


@app.get("/")
def root():
    return {"message": "Welcome to the Language Learning API! How can I help you today?"}


#OLD CODE WITHOUT THE DATABASE INTEGARTION
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # You can specify domains instead of "*" for security
#     allow_credentials=True,
#     allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
#     allow_headers=["*"],  # Allow all headers
# )

# API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
# HEADERS = {"Authorization": "Bearer Your API Key"}  

# class LessonRequest(BaseModel):
#     topic: str
#     language: str

# @app.get("/chat/")
# def chat_with_ai(prompt: str):
#     """Endpoint for AI chat."""
#     return {"response": chat(prompt)}

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
    
#     session_id = id(websocket)  # Generate a unique session ID

#     # ✅ Ensure session is initialized before usage
#     if session_id not in chat_sessions:
#         chat_sessions[session_id] = []  

#     try:
#         while True:
#             prompt = await websocket.receive_text()
#             response = chat(prompt, session_id)  # This calls the imported chat function
#             await websocket.send_text(response)
#     except WebSocketDisconnect:
#         print(f"WebSocket {session_id} disconnected.")
#     except Exception as e:
#         print(f"WebSocket Error: {e}")
#     finally:
#         # ✅ Clean up the session when WebSocket disconnects
#         chat_sessions.pop(session_id, None)

# @app.get("/generate_quiz/")
# async def quiz_endpoint():
#     """Auto-fetch latest lesson topic and generate quiz."""
#     latest_topic, latest_language = await fetch_latest_lesson()
    
#     if not latest_topic:
#         return {"error": "No lesson topic found in database."}

#     quiz = await generate_quiz()
#     return quiz
    
# @app.get("/")
# def root():
#     return {"message": "Welcome to the Language Learning API! How can I help you today?"}

