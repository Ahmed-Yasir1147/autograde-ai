from google import genai
from typing import List, Dict
from core.config import logger
from core.exceptions import IllegalFileSizeError, UnsupportedFileTypeError, FileValidationError, FileValidationErrors
from llama_cloud import LlamaCloud
from .document_reader import DocumentReader
from .exam_formatter import ExamFormatter
from .exam_grader import ExamGrader
import asyncio

class GradingPipeline:
    """A pipleline combining document reader, exam formatter and exam grader orchestrating the entire grading process."""

    def __init__(self, gemini_client: genai.Client, llama_cloud: LlamaCloud):
        self.document_reader = DocumentReader(llama_cloud)
        self.exam_formatter = ExamFormatter(gemini_client)
        self.exam_grader = ExamGrader(gemini_client)

    async def grade_exams(
            self, 
            exam_paper: bytes | str, 
            answer_papers: Dict[str, List[bytes]] | Dict[str, List[str]], # name & list of answer papers
            answer_key: bytes | str,
            instructions: str,
            concurrency: int = 3,
        ) -> tuple[List[str], List[str]]:
        """The main function to grade exams using the GradingPipeline."""
        # validation failure raises exception, where we collect the relevant file & API will pass it to the frontend
        failed_files = {}
        
        self._try_validation(exam_paper, "exam_paper", failed_files)
        self._try_validation(answer_key, "answer_key", failed_files)
        for filename, answer_paper in answer_papers.items():
            self._try_validation(answer_paper, filename, failed_files)

        if failed_files:
            logger.error(f"Failed to validate the following files: {failed_files}")
            raise FileValidationError(failed_files=failed_files)

        exam_paper_text = self.document_reader.read_doc(exam_paper, "examp_paper") if isinstance(exam_paper, bytes) else exam_paper
        formatted_exam_paper = self.exam_formatter.format_exam_paper(exam_paper_text)

        answer_key_text = self.document_reader.read_doc(answer_key, "answer_key") if isinstance(answer_key, bytes) else answer_key
        formatted_answer_key = self.exam_formatter.format_answer_key(answer_key_text, formatted_exam_paper)
        
        graded_answer_papers = []
        failed_answer_papers = []
        
        await self._grade_exams_concurrently(answer_papers, formatted_exam_paper, formatted_answer_key, instructions, concurrency, graded_answer_papers, failed_answer_papers)
        
        return (graded_answer_papers, failed_answer_papers)

    

    async def _grade_exams_concurrently(
            self, 
            answer_papers: Dict[str, List[bytes]] | Dict[str, List[str]], 
            formatted_exam_paper: str, 
            formatted_answer_key: str, 
            instructions: str, 
            concurrency: int, 
            graded_answer_papers: List[str], 
            failed_answer_papers: List[str]
        ):
        """Adds extra layer of concurrency to grade answer papers."""
        # Iterate through all papers and group them into batches of size concurrency, then grade the group concurrently
        counter = 0
        answer_paper_filenames = list(answer_papers.keys())
        answer_papers = list(answer_papers.values())
        while counter < len(answer_papers):
            # Create a task group to grade the concurreny number of answer papers concurrently
            async with asyncio.TaskGroup() as tg:
                for i in range(0, concurrency):
                    counter += 1
                    # Break the loop if the counter exceeds the number of answer papers
                    if counter > len(answer_papers):
                        break
                    tg.create_task(
                        self._grade_exam(
                            answer_papers[counter - 1], 
                            answer_paper_filenames[counter - 1], # filename is used for logging
                            formatted_exam_paper, 
                            formatted_answer_key, 
                            instructions, 
                            graded_answer_papers, 
                            failed_answer_papers
                        )
                    )

    async def _grade_exam(
            self, 
            answer_paper: bytes | str, 
            answer_paper_filename: str,
            formatted_exam_paper: str, 
            formatted_answer_key: str, 
            instructions: str, 
            graded_answer_papers: List[str], 
            failed_answer_papers: List[str]
        ):
        """Formats and grade single answer paper."""
        try:
            if isinstance(answer_paper, bytes):
                answer_paper_text = await asyncio.to_thread(self.document_reader.read_doc, answer_paper, answer_paper_filename)
            else:
                answer_paper_text = answer_paper
            formatted_answer_paper = await asyncio.to_thread(
                self.exam_formatter.format_answer_paper, 
                answer_paper_text, 
                formatted_exam_paper,
                answer_paper_filename
            )
            graded_answer_paper = await asyncio.to_thread(
                self.exam_grader.grade_exam_paper, 
                formatted_exam_paper, 
                formatted_answer_paper, 
                formatted_answer_key, 
                instructions,
                answer_paper_filename
            )
            graded_answer_papers.append(graded_answer_paper)
        except Exception as e:
            logger.error(f"An error occurred while grading the answer paper {answer_paper_filename}: {e}")
            failed_answer_papers.append(graded_answer_paper)

    def _try_validation(
            self, 
            file_bytes: str| bytes, 
            file_name: str = "", 
            failed_files: dict[str, FileValidationErrors] = {}
        ):
        """Validates if file_bytes is a valid file and adds it to failed_files if not."""
        if isinstance(file_bytes, bytes):
            try:
                self.document_reader.validate_doc(file_bytes, file_name)
            except IllegalFileSizeError as e:
                failed_files[file_name] = FileValidationErrors.ILLEGAL_FILE_SIZE
            except UnsupportedFileTypeError as e:
                failed_files[file_name] = FileValidationErrors.UNSUPPORTED_FILE_TYPE