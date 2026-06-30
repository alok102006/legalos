import os
import aiofiles
from app.config import settings

# Directory for storing uploaded files locally
UPLOAD_DIR = "./uploads"

async def save_file(filename: str, content: bytes) -> str:
    """
    Saves file bytes to local storage directory.
    Returns the absolute or relative path to the saved file.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    # Simple sanitization of filename to avoid path traversal
    safe_filename = os.path.basename(filename)
    # Append timestamp or simple identifier if name collides
    file_path = os.path.join(UPLOAD_DIR, safe_filename)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
        
    return file_path


async def delete_file(storage_path: str) -> None:
    """Removes a file from local storage."""
    try:
        if os.path.exists(storage_path):
            os.remove(storage_path)
    except Exception as e:
        print(f"[STORAGE] Failed to delete file {storage_path}: {e}")
