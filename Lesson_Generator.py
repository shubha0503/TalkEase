import requests
import os
import re
import random
API_URL = "https://router.huggingface.co/hf-inference/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": "Bearer Your API key"}  # Replace with your API key
    
# def format_prompt(topic, language):
#     """Format user input to instruct Mixtral to generate a language lesson."""
#     # return f"Create a beginner-friendly lesson on '{topic}' in '{language}'. Make it engaging with examples."
#     return f"Teach me about '{topic}' in '{language}'. Explain it in a beginner-friendly way with examples and pronunciation (if applicable). Keep it short, clear, and practical for daily use."
    
# def clean_text(response):
#     """Removes instruction markers, redundant prompt text, and shortens output."""
#     cleaned = response.replace("<s>", "").replace("[INST]", "").replace("[/INST]", "").strip()
    
#     # Remove redundant prompt at the beginning
#     if "Create a beginner-friendly lesson" in cleaned:
#         cleaned = cleaned.split("Create a beginner-friendly lesson", 1)[-1].strip()
    
#     # Trim long responses while keeping key info
#     lines = cleaned.split("\n")  
#     if len(lines) > 15:  # Limit to 15 lines max
#         cleaned = "\n".join(lines[:15]) 
#     return cleaned

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


def clean_text(response):
    """Cleans and formats AI-generated text for better readability."""
    
    # Remove unwanted AI instructions & placeholders
    response = re.sub(r".*?Ensure variety in wording and examples each time\.", "", response, flags=re.DOTALL).strip()
    response = response.replace("<s>", "").replace("[INST]", "").replace("[/INST]", "").strip()

    # Ensure section labels are correctly formatted  
    response = re.sub(r"\*\*\s*(Introduction|Key Words & Meanings|Explanation|Examples|Engagement)\s*\*\*", r"\n**\1**", response)

    # Fix bullet points with proper spacing
    response = response.replace("- ", "\n- ")  

    # Ensure alternate line formatting
    start_match = re.search(r"1️⃣", response)
    if start_match:
        response = response[start_match.start():]

    # Remove extra markdown clutter
    response = re.sub(r"\*\*([^\*]+)\*\*", r"**\1**", response)  # Fix bold text 
    response = re.sub(r"<s>|</s>|\[INST\]|\[/INST\]", "", response).strip()

    # Ensure proper bullet point formatting
    response = response.replace("- ", "\n- ")  

    # Remove any stray headers or unwanted markdown
    response = re.sub(r"#+", "", response) 

    return response.strip()

def generate_lesson(topic, language):
    """Sends request to Mixtral API for a fresh, structured lesson."""
    prompt = format_prompt(topic, language)
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_length": 300,   # Allow slightly longer responses for detail
            "temperature": 1.0,  # Increase randomness for variation
            "top_p": 0.85        # Control diversity without losing coherence
        }
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=payload)
        response.encoding = 'utf-8'  
        response.raise_for_status()
        
        result = response.json()
        
        if isinstance(result, list) and "generated_text" in result[0]:
            return clean_text(result[0]["generated_text"])
        else:
            return "Error: Unexpected response format"
    
    except requests.exceptions.RequestException as e:
        return f"API Error: {str(e)}"



# def generate_lesson(topic, language):
#     """Sends request to Mixtral API to generate a structured lesson."""
#     prompt = format_prompt(topic, language)
    
#     try:
#         response = requests.post(API_URL, headers=HEADERS, json={"inputs": prompt})
#         response.encoding = 'utf-8'  
#         response.raise_for_status() # Raise error for bad response status
        
#         result = response.json()
        
#         if isinstance(result, list) and "generated_text" in result[0]:
#             return clean_text(result[0]["generated_text"])
#         else:
#             return "Error: Unexpected response format"
    
#     except requests.exceptions.RequestException as e:
#         return f"API Error: {str(e)}"




# ✅ Test API Response
# if __name__ == "__main__":
#     topic = "Basic Greetings"
#     language = "Japanese"
#     print(generate_lesson(topic, language))
