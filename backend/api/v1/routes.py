import sys
import pathlib

# resetting path for easy importing
current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(current_dir.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from core.config import logger, GEMINI_API_KEY, GRADING_SCHEME
from core.exceptions import FileValidationError
from services.grading_pipeline import GradingPipeline
from models.routes_schemas import FilePayload
from models.routes_schemas import GradingRequest, GradingResponse
from llama_cloud import LlamaCloud
from google import genai

llama_cloud = LlamaCloud()
gemini_client = genai.Client(api_key=GEMINI_API_KEY)

grading_pipeline = GradingPipeline(gemini_client, llama_cloud)

router = APIRouter(prefix="/api/v1")

@router.post("/grade_exams")
async def grade_exams(
    grading_request: GradingRequest
) -> GradingResponse:
    """Main route to grade exams using the GradingPipeline"""
    exam_paper = to_text_or_bytes(grading_request.exam_paper)
    answer_key = to_text_or_bytes(grading_request.answer_key)
    answer_papers = {}
    for key, value in grading_request.answer_papers.items():
        answer_papers[key] = to_text_or_bytes(value)
    try:
        grading_response = await grading_pipeline.grade_exams(
            exam_paper,
            answer_papers,
            answer_key,
            grading_request.instructions,
            grading_request.grading_scheme,
            grading_request.concurrency
        )
        return grading_response
    # only FileValidationError in normal flow is thrown by GradingPipeline
    except FileValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail={
                "message": e.message,
                "failed_files": e.failed_files
            }
        )
    # in case of any unexpected error
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail={
                "message": f"An error occurred while grading the exam: {e}"
            }
        )


@router.get("/get_grading_scheme")
async def get_grading_scheme():
    """Send grading scheme to frontend"""
    return GRADING_SCHEME

# utility function to convert FilePayload to str or bytes 
def to_text_or_bytes(item: str | FilePayload) -> str | bytes:
    return item if isinstance(item, str) else item.data