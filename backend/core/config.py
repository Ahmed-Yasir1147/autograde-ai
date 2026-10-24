import os
from pathlib import Path
import logging

# API metadata
APP_TITLE = "Autograde AI"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
    Autograde AI is an AI-powered exam grading system that automates the evaluation of student answer papers, providing accurate and efficient grading for both objective and subjective questions. 
    It leverages advanced natural language processing techniques to assess answers based on predefined criteria, ensuring consistency and fairness in grading.
    """

# File upload configuration
MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Supported MIME types
SUPPORTED_MIME_TYPES = {
    "application/pdf": "pdf",
    "application/msword": "doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "image/png": "png",
    "image/jpeg": "jpeg",
    "image/jpg": "jpg",
    "image/webp": "webp",
    "application/octet-stream": "binary",
}
SUPPORTED_EXTENSIONS = {".pdf", ".doc", ".docx", ".png", ".jpeg", ".jpg", ".webp"}

# GEMINI & LlamaIndex Model configuration
GEMINI_STANDARD_MODEL_CODE = "gemini-3.5-flash-lite"
GEMINI_FALLBACK_MODEL_CODE = "gemini-3.1-flash-lite"
LLAMA_CLOUD_TIER = "cost_effective"
LLAMA_CLOUD_VERSION = "latest"

# Models API kEYS
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("llama_cloud").setLevel(logging.WARNING)

# Grading configuration
GRADING_SCHEME = {
    "A+": (100, 95),
    "A": (94, 90),
    "B+": (89, 85),
    "B": (84, 80),
    "C+": (79, 75),
    "C": (74, 70),
    "D": (69, 60),
    "E": (59, 50),
    "F": (49, 0),
}




