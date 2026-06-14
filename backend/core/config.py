import os
from dotenv import load_dotenv
from pathlib import Path

# Only used locally — Railway injects env variables directly
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# --- Database ---
SUPABASE_CONNECTION_STRING = os.getenv("SUPABASE_CONNECTION_STRING")

# --- OpenAI ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Groq ---
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# --- Validate all required keys are present ---
REQUIRED_VARS = {
    "SUPABASE_CONNECTION_STRING": SUPABASE_CONNECTION_STRING,
    "OPENAI_API_KEY": OPENAI_API_KEY,
    "GROQ_API_KEY": GROQ_API_KEY,
}

missing = [key for key, val in REQUIRED_VARS.items() if not val]
if missing:
    raise EnvironmentError(f"Missing environment variables: {missing}")