from llama_cloud import LlamaCloud, RateLimitError
from core.config import LLAMA_CLOUD_TIER, LLAMA_CLOUD_VERSION, logger
from core.exceptions import ModelLimitReachedError, FileProcessingError, UnsupportedFileTypeError, IllegalFileSizeError
import time
from core.config import MAX_FILE_SIZE_BYTES, SUPPORTED_MIME_TYPES
import magic
from utils.helper_functions import singleton

@singleton
class DocumentReader:
    """A class to read and parse documents using the LlamaCloud API."""

    def __init__(self, llama_cloud: LlamaCloud):
        self.client = llama_cloud

    def validate_doc(self, file_bytes: bytes, file_name: str = ""):
        """Check if document follows MIME type and size constraints"""

        file_size = len(file_bytes)
        if file_size > MAX_FILE_SIZE_BYTES:
            logger.error(f"File {file_name} size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes.")
            raise IllegalFileSizeError(f"File {file_name} size exceeds maximum allowed size of {MAX_FILE_SIZE_BYTES} bytes.", file_name)
        elif file_size == 0:
            logger.error(f"File {file_name} is empty.")
            raise IllegalFileSizeError(f"File {file_name} is empty.", file_name)

        mime_type = magic.from_buffer(file_bytes, mime=True)
        if mime_type not in SUPPORTED_MIME_TYPES:
            logger.error(f"File {file_name} has unsupported MIME type: {mime_type}")
            raise UnsupportedFileTypeError(f"File {file_name} Unsupported MIME type: {mime_type}", file_name)

    def read_doc(self, file_bytes: bytes, file_name: str = ""):
        """Reads and parses a document from bytes using the LlamaCloud API and returns the extracted text."""
        try_count = 1
        logger.info(f"Reading file {file_name}")
        while True:
            try: 
                file = self.client.files.create(file=file_bytes, purpose="parse")
                result = self.client.parsing.parse(
                    file_id=file.id,
                    tier=LLAMA_CLOUD_TIER,
                    version=LLAMA_CLOUD_VERSION,
                    expand=["markdown"],
                )
                text = ""
                for page in result.markdown.pages:
                    text += page.markdown
                return text
            except RateLimitError:
                logger.warning(f"Rate limit reached. Retrying in {try_count * 2} seconds...")
                time.sleep(try_count * 2) 
                try_count *= 1
                # Max retry: 3
                if try_count > 3:
                    logger.error("Exceeded maximum retry attempts due to rate limit.")
                    raise ModelLimitReachedError(model_name="LlamaIndex")
            except Exception as e:
                logger.error(f"An error occurred while reading the document: {e}")
                raise FileProcessingError()
 

        