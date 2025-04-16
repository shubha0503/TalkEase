import random
import re
import requests
import httpx
from google.cloud import firestore

API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer YOUR HF KEY"}  # Replace with your API key

# Firestore DB client
db = firestore.Client()

# -------------------- FORMAT PROMPT -------------------- #
def format_prompt(topic, language):
    """Format user input to instruct Mixtral to generate a structured, varied lesson."""
    variations = [
        "Provide a beginner-friendly lesson on",
        "Generate an interactive language lesson about",
        "Create a structured and engaging lesson covering",
        "Write a simple and easy-to-follow lesson on"
    ]
    
    return (
        f"{random.choice(variations)} '{topic}' in '{language}'. "
        "Ensure variety in wording and examples each time. "
        "Structure it like this:\n"
        "1️⃣ **Introduction**: One sentence introducing the topic.\n"
        "2️⃣ **Key Words & Meanings**: Bullet points with simple definitions.\n"
        "3️⃣ **Explanation**: A short and clear explanation with examples.\n"
        "4️⃣ **Examples**: Real-life sentences with translations.\n"
        "5️⃣ **Engagement**: A fun tip, daily usage, or interactive exercise.\n"
        "👉 Make it clear, structured, and concise while **avoiding repetition**."
    )

# -------------------- CLEAN RESPONSE -------------------- #
def clean_text(response):
    """Cleans and formats AI-generated text for better readability."""
    response = re.sub(r".*?Ensure variety in wording and examples each time\.", "", response, flags=re.DOTALL).strip()
    response = response.replace("<s>", "").replace("[INST]", "").replace("[/INST]", "").strip()
    response = re.sub(r"\*\*\s*(Introduction|Key Words & Meanings|Explanation|Examples|Engagement)\s*\*\*", r"\n**\1**", response)
    response = response.replace("- ", "\n- ")  
    start_match = re.search(r"1️⃣", response)
    if start_match:
        response = response[start_match.start():]
    response = re.sub(r"\*\*([^\*]+)\*\*", r"**\1**", response)
    response = re.sub(r"<s>|</s>|\[INST\]|\[/INST\]", "", response).strip()
    response = response.replace("- ", "\n- ")  
    response = re.sub(r"#+", "", response) 
    return response.strip()

# -------------------- FIREBASE SAVE -------------------- #
async def store_lesson_in_firestore(topic: str, language: str, lesson: str):
    lesson_data = {
        "topic": topic,
        "language": language,
        "lesson": lesson,
        "timestamp": firestore.SERVER_TIMESTAMP
    }
    db.collection("lessons").add(lesson_data)

# -------------------- LESSON GENERATOR -------------------- #
async def generate_lesson(topic, language):
    """Sends request to Mixtral API, cleans it, and stores it in Firestore."""
    prompt = format_prompt(topic, language)

    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 300,
            "temperature": 1.0,
            "top_p": 0.85
        }
    }

    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.encoding = 'utf-8'
        response.raise_for_status()
        result = response.json()

        if isinstance(result, list) and "generated_text" in result[0]:
            lesson = clean_text(result[0]["generated_text"])
            
            # ✅ AWAIT the Firestore save
            await store_lesson_in_firestore(topic, language, lesson)
            
            return lesson
        else:
            return "Error: Unexpected response format"

    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"

