import requests
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI()

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer YOUR HF KEY"}  # Replace with your API key

import uuid
from google.cloud import firestore

db = firestore.Client()

chat_sessions = {}

async def store_chat_message(session_id: str, user_input: str, ai_response: str):
    chat_data = {
        "session_id": session_id,
        "user_input": user_input,
        "ai_response": ai_response,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("chats").add(chat_data)

async def chat(prompt: str, session_id=None):
    if session_id and session_id in chat_sessions:
        chat_sessions[session_id].append(f"User: {prompt}")
        conversation_history = "\n".join(chat_sessions[session_id][-5:])
        formatted_prompt = f"You are TalkEase, a friendly language tutor who speaks and teaches multiple languages fluently (like English, Hindi, French, Spanish, German, Japanese, Korean, Italian, Chinese, Russian, Arabic, and more). If asked how many languages do you know? or similar questions, always list the actual languages. When teaching, switch to the target language and give short, friendly examples. Now continue the conversation naturally based on the last few messages.Respond concisely and stay on topic. Avoid Repetation of one thing again and again in the chat. The respose has to be varied and and there should be randomness in response to same question. Also the response has to be short and precise:\n{conversation_history} [/INST]"
    else:
        formatted_prompt = f"You are TalkEase, a friendly language tutor who speaks and teaches multiple languages fluently (like English, Hindi, French, Spanish, German, Japanese, Korean, Italian, Chinese, Russian, Arabic, and more). If asked how many languages do you know? or similar questions, always list the actual languages. When teaching, switch to the target language and give short, friendly examples. Now continue the conversation naturally based on the last few messages.Respond concisely and stay on topic. Avoid Repetation of one thing again and again in the chat. The respose has to be varied and and there should be randomness in response to same question. Also the response has to be short and precise: {prompt} [/INST]"
    payload = {
        "inputs": formatted_prompt,
        "parameters": {"max_length": 80, "temperature": 0.7, "top_p": 0.8}  # Shorter and more controlled output
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        
        bot_response = result[0]["generated_text"] if isinstance(result, list) else "Error: Unexpected response format"
        if prompt in bot_response:
             bot_response = bot_response.split(prompt, 1)[-1].strip()


        # Ensure bot response is relevant & doesn’t repeat
        bot_response = bot_response.strip().split("\n")[-1]  # Get the last relevant line
        bot_response = bot_response.replace("[INST]", "").replace("[/INST]", "").strip()
        bot_response = bot_response.replace(prompt, "").strip()  # Remove echoed user input if present
        bot_response = bot_response.replace("User:", "").replace("Bot:", "").strip()

        if session_id:
            chat_sessions[session_id].append(f"Bot: {bot_response}")
        
        # Save the chat exchange to Firestore
        await store_chat_message(str(session_id), prompt, bot_response)

        return bot_response
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"
