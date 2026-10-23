import sys
import pathlib

# resetting path for easy importing
current_dir = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(current_dir.parent.parent))

from fastapi import APIRouter, Depends, HTTPException, status
from core.config import logger, GEMINI_API_KEY
from core.exceptions import FileValidationError
from services.grading_pipeline import GradingPipeline
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
    try:
        graded_answer_papers, failed_answer_papers = await grading_pipeline.grade_exams(
            grading_request.exam_paper,
            grading_request.answer_papers,
            grading_request.answer_key,
            grading_request.instructions,
            grading_request.concurrency
        )
        return GradingResponse(
            graded_answer_papers=graded_answer_papers,
            failed_answer_papers=failed_answer_papers
        )
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