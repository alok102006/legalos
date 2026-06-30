import json
import httpx
from app.config import settings

def generate_local(prompt: str, system: str = "", json_mode: bool = False) -> str:
    """
    Stub for a local LLM provider (Ollama / vLLM / OpenAI-compatible endpoint).
    By default, it tries to connect to Ollama at http://localhost:11434/v1.
    If it fails, it returns a mocked local response.
    """
    url = "http://localhost:11434/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "model": "llama3",  # default Ollama model name
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.0
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
        
    try:
        # Short timeout to avoid blocking the main server if Ollama is not running
        with httpx.Client(timeout=5.0) as client:
            response = client.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Local LLM connection failed or Ollama not running ({str(e)}). Using fallback stub.")
    
    # Fallback mocked response if local LLM server is not active
    if json_mode:
        return json.dumps({
            "status": "mocked_local_response",
            "summary": "This is a mocked local LLM response because Ollama is not active at http://localhost:11434",
            "risk_type": "none",
            "risk_score": 0
        })
    else:
        return "This is a fallback mocked local response. Please verify Ollama is running."
