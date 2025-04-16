from fastapi import FastAPI, Depends
import firebase_admin
from firebase_admin import credentials, firestore
import httpx 
from google.cloud import firestore

# Constants (tune yeh apne actual values se replace karni hongi)
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {
    "Authorization": "Bearer yoou hf key",
    "Content-Type": "application/json"
}

# cred = credentials.Certificate("C:/Users/hp/Downloads/talkease-d404e-firebase-adminsdk-fbsvc-cc6f68df96.json")
# firebase_admin.initialize_app(cred)
db = firestore.Client()  

async def fetch_latest_lesson():
    lessons_ref = db.collection("lessons").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    docs = lessons_ref.stream()
    
    for doc in docs:
        data = doc.to_dict()
        print(f"📌 Fetched Lesson Data: {data}")
        return data.get("topic"), data.get("language")

    return None, None  

async def generate_quiz():
    lesson_topic, lesson_language = await fetch_latest_lesson()
    
    if not lesson_topic:
        return {"error": "No lesson topic found in database."}

    prompt = f"""
    Create a language quiz for the topic: "{lesson_topic}" in "{lesson_language}".
    The quiz should include:
    - 2 Multiple Choice Questions (MCQs)
    - 2 Fill in the Blanks
    - 1 Sentence Rearrangement
    - 1 Pronunciation word
    
    **Ensure the response is in valid JSON format only. Example:**
    {{
        "mcqs": [
            {{"question": "What is ...?", "options": ["A", "B", "C", "D"], "answer": "A"}}
        ],
        "fill_in_blanks": [
            {{"sentence": "I ____ Spanish.", "answer": "speak"}}
        ],
        "sentence_rearrangement": [
            {{"jumbled": "Hola! estás cómo", "answer": "¡Hola! ¿Cómo estás?"}}
        ],
        "pronunciation": [
            {{"word": "Encantado"}}
        ]
    }}
    """

    print(f"📌 Quiz Prompt Sent: {prompt}")

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                API_URL,
                json={"inputs": prompt},
                headers=HEADERS
            )
            response.raise_for_status()
            print(f"📌 Quiz API Response: {response.json()}")
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}", "details": e.response.text}
        except httpx.TimeoutException:
            return {"error": "Request timed out. Try again later."}
