import os
import time
from app.config import settings

# Global reference for the singleton
_embedder_instance = None

class Embedder:
    """
    Singleton wrapper around sentence-transformers/all-MiniLM-L6-v2.
    - Cached to a project-local folder (via HF_HOME/SENTENCE_TRANSFORMERS_HOME).
    - Loaded once per process.
    """
    def __init__(self):
        # Apply environment settings to cache folders before importing/loading model
        os.environ["HF_HOME"] = settings.hf_home
        os.environ["SENTENCE_TRANSFORMERS_HOME"] = settings.sentence_transformers_home
        
        # Check if the cache path already exists and has model files
        # Sentence-transformers usually stores them under models--sentence-transformers--all-MiniLM-L6-v2
        cache_dir = settings.hf_home
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        
        is_cached = False
        if os.path.exists(cache_dir) and len(os.listdir(cache_dir)) > 0:
            is_cached = True
            
        print(f"[EMBEDDER] Initializing {model_name}...")
        if is_cached:
            print(f"[EMBEDDER] Cache directories found in {cache_dir}. Attempting loading from local cache...")
        else:
            print(f"[EMBEDDER] Cache directory empty or missing. Model will download from HuggingFace to {cache_dir}...")
            
        start_time = time.time()
        # Defer import of SentenceTransformer until runtime loading to keep CLI scripts snappy
        from sentence_transformers import SentenceTransformer
        
        self.model = SentenceTransformer(model_name, cache_folder=cache_dir)
        elapsed = time.time() - start_time
        print(f"[EMBEDDER] Loaded {model_name} in {elapsed:.2f}s (Cache Hit: {is_cached})")

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generates 384-dimensional vector embeddings for a list of texts."""
        if not texts:
            return []
        
        # sentence-transformers encode returns a numpy array or list of lists
        embeddings = self.model.encode(texts, convert_to_numpy=True)
        return embeddings.tolist()


def get_embedder() -> Embedder:
    """Gets the global Embedder singleton. Initializes it if not already loaded."""
    global _embedder_instance
    if _embedder_instance is None:
        _embedder_instance = Embedder()
    return _embedder_instance
