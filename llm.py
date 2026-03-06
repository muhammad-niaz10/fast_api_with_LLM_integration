import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("API key missing! Add GEMINI_API_KEY in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

def ask_openai(prompt: str) -> str: 
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print("LLM Error:", e)
        return f"Error: {str(e)}"
