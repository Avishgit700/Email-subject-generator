from typing import Optional
import os, requests
import streamlit as st

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "tinyllama")
TIMEOUT_S  = int(os.getenv("OLLAMA_TIMEOUT", "180"))
MAX_TOKENS = int(os.getenv("OLLAMA_MAX_TOKENS", "80"))

@st.cache_resource(show_spinner=True)
def get_generator(temperature: float = 0.8, seed: Optional[int] = None):
    def generate(prompt: str, max_new_tokens: int = MAX_TOKENS) -> str:
        payload = {
            "model": MODEL_NAME,
            "prompt": prompt,
            "options": {"temperature": float(temperature), "num_predict": int(max_new_tokens)},
            "stream": False
        }
        r = requests.post(f"{OLLAMA_URL}/api/generate", json=payload, timeout=TIMEOUT_S)
        r.raise_for_status()
        return (r.json().get("response") or "").strip()
    return generate
