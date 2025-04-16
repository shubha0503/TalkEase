import httpx
from google.cloud import firestore

db = firestore.Client()  # Firestore Client Initialize

# Your API details for quiz generation
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer YOU HF KEY"}  

async def fetch_latest_lesson():
    """Fetch the latest lesson from Firestore."""
    lessons_ref = db.collection("lessons").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(1)
    docs = lessons_ref.stream()
    
    for doc in docs:
        data = doc.to_dict()
        return data.get("topic"), data.get("language")  # Return both topic & language
    
    return None, None

async def generate_quiz():
    """Generate a quiz based on the latest learned lesson."""
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

    async with httpx.AsyncClient(timeout=30) as client:
        try:
            response = await client.post(
                API_URL,
                json={"inputs": prompt},
                headers=HEADERS
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP error {e.response.status_code}", "details": e.response.text}
        except httpx.TimeoutException:
            return {"error": "Request timed out. Try again later."}

