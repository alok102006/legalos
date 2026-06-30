import os
from google import genai
from google.genai import types
from app.config import settings

# Initialize Client.
# The SDK automatically uses GEMINI_API_KEY from environment if api_key is not passed,
# but we pass settings.gemini_api_key explicitly for reliability.
_client = None

def get_gemini_client():
    global _client
    if _client is None:
        api_key = settings.gemini_api_key
        if not api_key:
            # Fallback to os.environ just in case settings didn't load it
            api_key = os.environ.get("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in settings or environment.")
        
        # Instantiate the new google-genai Client
        _client = genai.Client(api_key=api_key)
    return _client


def generate_gemini(prompt: str, system: str = "", json_mode: bool = False) -> str:
    """Generate response using Google's Gemini model via the google-genai SDK."""
    client = get_gemini_client()
    
    # We use gemini-2.5-flash as the standard fast LLM model
    model_name = "gemini-2.5-flash"
    
    config = types.GenerateContentConfig(
        system_instruction=system if system else None,
        response_mime_type="application/json" if json_mode else "text/plain"
    )
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=config
        )
        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        raise e
