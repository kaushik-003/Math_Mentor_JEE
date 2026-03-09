"""
Central configuration for Math Mentor.
All thresholds, model names, and constants live here.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Model Config ---
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "whisper-1")
LLM_TEMPERATURE = 0.2  # Low temp for math accuracy

# --- Confidence Thresholds ---
OCR_CONFIDENCE_THRESHOLD = 0.7       # Below this → HITL triggered for OCR
ASR_CONFIDENCE_THRESHOLD = 0.7       # Below this → HITL triggered for audio
VERIFIER_CONFIDENCE_THRESHOLD = 0.75 # Below this → HITL triggered for verification
MEMORY_SIMILARITY_THRESHOLD = 0.85   # Above this → "similar problem found"

# --- RAG Config ---
CHROMA_KNOWLEDGE_COLLECTION = "math_knowledge"
CHROMA_MEMORY_COLLECTION = "past_solutions"
RAG_TOP_K = 5
CHUNK_SIZE = 500        # characters per chunk
CHUNK_OVERLAP = 50      # overlap between chunks

# --- Agent Config ---
MAX_REFINER_ITERATIONS = 1  # Cap refinement loops for speed
MAX_SOLVER_RETRIES = 2      # If SymPy tool fails, retry this many times

# --- Supported Topics ---
SUPPORTED_TOPICS = [
    "algebra",
    "probability",
    "calculus",
    "linear_algebra",
]

# --- File Paths ---
KNOWLEDGE_DIR = "data/knowledge"
MEMORY_FILE = "memory/memory.json"
CHROMA_PERSIST_DIR = "data/chroma_db"

