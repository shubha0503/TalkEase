import requests
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from pydantic import BaseModel
import uvicorn
import os

app = FastAPI()

# API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer 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"}  # Replace with your API key

#for main.py

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
    



#for app2222.py

# def chat(prompt: str):
#     """Sends a dynamic request to Mixtral API for varied responses."""
#     payload = {
#         "inputs": f"<s> [INST] {prompt} Provide a detailed and varied response. Avoid repetition. [/INST]",
#         "parameters": {"max_length": 150, "temperature": 0.8, "top_p": 0.9}  # Adjust for more randomness
#     }
    
#     try:
#         response = requests.post(API_URL, headers=HEADERS, json=payload)
#         response.raise_for_status()
#         result = response.json()
        
#         return result[0]["generated_text"] if isinstance(result, list) else "Error: Unexpected response format"
#     except requests.exceptions.RequestException as e:
#         return f"API Error: {str(e)}"


import requests

chat_sessions = {}

def chat(prompt: str, session_id=None):
    """Sends a refined request to Mixtral API for better, concise, and relevant responses."""
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []  # Initialize session if not existing
    
    # Store user message
    chat_sessions[session_id].append(f"User: {prompt}")

    # Keep only the last 3 exchanges for context (reduces weird repetition)
    conversation_history = "\n".join(chat_sessions[session_id][-3:])  

    # More precise instructions to AI
    formatted_prompt = f"<s> [INST] Respond concisely and stay on topic also the response has to be short and precise:\n{conversation_history} [/INST]"

    payload = {
        "inputs": formatted_prompt,
        "parameters": {"max_length": 50, "temperature": 0.7, "top_p": 0.8}  # Shorter and more controlled output
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.raise_for_status()
        result = response.json()
        
        bot_response = result[0]["generated_text"] if isinstance(result, list) else "Error: Unexpected response format"

        # Ensure bot response is relevant & doesn’t repeat
        bot_response = bot_response.strip().split("\n")[-1]  # Get the last relevant line
        bot_response = bot_response.replace("[INST]", "").replace("[/INST]", "").strip()
        bot_response = bot_response.replace(prompt, "").strip()  # Remove echoed user input if present
        bot_response = bot_response.replace("User:", "").replace("Bot:", "").strip()

        # Store bot response
        chat_sessions[session_id].append(f"Bot: {bot_response}")

        return bot_response
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"
