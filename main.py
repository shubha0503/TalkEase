import requests
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect, Depends
from pydantic import BaseModel
from ChatBot import store_chat_message, chat, chat_sessions 
from Lesson_Generator import generate_lesson, store_lesson_in_firestore
import firebase_admin
from firebase_admin import credentials, firestore
import httpx
import os
from google.cloud import firestore
from Quiz import generate_quiz
from Quiz import fetch_latest_lesson

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/hp/Desktop/Project/Talk-Ease/talkease-d404e-firebase-adminsdk-fbsvc-899cf3b3c0.json"
cred = credentials.Certificate("C:/Users/hp/Desktop/Project/Talk-Ease/talkease-d404e-firebase-adminsdk-fbsvc-899cf3b3c0.json")
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
async def get_chat(prompt: str):
    response = await chat(prompt)
    return {"response": response}

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    
    session_id = str(id(websocket))  # Unique session ID as string
    chat_sessions[session_id] = []

    while True:
        prompt = await websocket.receive_text()
        response = await chat(prompt, session_id)  # await here!
        await websocket.send_text(response)


@app.post("/generate_lesson/")
async def generator(request: LessonRequest):
    """API Endpoint to generate and store a lesson."""
    lesson = await generate_lesson(request.topic, request.language)
    
    if "API Error" in lesson:
        raise HTTPException(status_code=500, detail=lesson)
    
    await store_lesson_in_firestore(request.topic, request.language, lesson)  # Store in Firestore
    return {"topic": request.topic, "language": request.language, "lesson": lesson}


@app.get("/generate_quiz/")
async def quiz_endpoint():
    """Auto-fetch latest lesson topic and generate quiz."""
    quiz = await generate_quiz()
    
    if "error" in quiz:
        raise HTTPException(status_code=500, detail=quiz["error"])
    
    return quiz

@app.get("/")
def root():
    return {"message": "Welcome to the Language Learning API! How can I help you today?"}
