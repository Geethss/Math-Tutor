import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_KEY_HERE")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PHASE1_PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "phase1_prompt.txt")
PHASE2_PROMPT_PATH = os.path.join(BASE_DIR, "prompts", "phase2_prompt.txt")
STATIC_OUTPUT_DIR = os.path.join(BASE_DIR, "static", "output")
