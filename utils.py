import os
import json
from openai import OpenAI
from pinecone import Pinecone

# --- טעינת קונפיגורציה ---
def load_config():
    """טוען את קובץ הקונפיגורציה"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_paths = [
        os.path.join(current_dir, 'rag_config.json'),  # מהתיקייה הנוכחית
        'rag_config.json',  # מהתיקייה הנוכחית (working directory)
    ]
    
    for config_path in config_paths:
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return json.load(f)
    
    raise FileNotFoundError(f"Could not find rag_config.json. Checked paths: {config_paths}")

CONFIG = load_config()

# --- אתחול לקוחות ---
def get_openai_client():
    """מחזיר לקוח OpenAI"""
    return OpenAI(
        api_key=os.environ.get("LLMOD_API_KEY"),
        base_url="https://api.llmod.ai/v1"
    )

def get_pinecone_index():
    """מחזיר את אינדקס Pinecone"""
    pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))
    
    # חילוץ שם האינדקס מה-URL או משתמש ישירות בשם האינדקס
    index_host = os.environ.get("PINECONE_INDEX_HOST", "")
    if index_host:
        # חילוץ שם האינדקס מה-URL: https://index-name-xxx.svc.xxx.pinecone.io
        # או אם נתנו רק את השם, נשתמש בו ישירות
        if index_host.startswith("http"):
            # חילוץ משם האינדקס מה-URL
            index_name = index_host.split("://")[1].split(".")[0]
        else:
            # אם זה כבר שם האינדקס
            index_name = index_host
    else:
        # נסה מהקונפיגורציה
        index_name = CONFIG.get("index_name", "ted-talks-rag")
    
    return pc.Index(index_name)

# --- מודלים ---
EMBEDDING_MODEL = "RPRTHPB-text-embedding-3-small"
CHAT_MODEL = "RPRTHPB-gpt-5-mini"

# --- System Prompt (חובה לפי המטלה) ---
SYSTEM_PROMPT = """You are a TED Talk assistant that answers questions strictly and
only based on the TED dataset context provided to you (metadata
and transcript passages).
You must not use any external
knowledge, the open internet, or information that is not explicitly
contained in the retrieved context.
If the answer cannot be
determined from the provided context, respond: "I don't know
based on the provided TED data."
Always explain your answer
using the given context, quoting or paraphrasing the relevant
transcript or metadata when helpful.
You may add additional clarifications (e.g., response style), but you must
keep the above constraints."""

