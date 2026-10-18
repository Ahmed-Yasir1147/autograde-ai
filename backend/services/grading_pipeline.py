from google import genai
from typing import List, Dict
from core.config import logger
from llama_cloud import LlamaCloud
from document_reader import DocumentReader
from exam_formatter import ExamFormatterGemini
from exam_grader import ExamGrader
import asyncio

class GradingPipeline:
    """A pipleline combining document reader, exam formatter and exam grader orchestrating the entire grading process."""

    def __init__(self, gemini_client: genai.Client, llama_cloud: LlamaCloud):
        self.document_reader = DocumentReader(llama_cloud)
        self.exam_formatter = ExamFormatterGemini(gemini_client)
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
        # validation failure raises exception which stops pipeline & API will pass it to the frontend
        self.document_reader.validate_doc(exam_paper, "exam_paper")
        self.document_reader.validate_doc(answer_key, "answer_key")
        for filename, answer_paper in answer_papers.items():
            self.document_reader.validate_doc(answer_paper, filename)


        exam_paper_text = self.document_reader.read_doc(exam_paper) if isinstance(exam_paper, bytes) else exam_paper
        formatted_exam_paper = self.exam_formatter.format_exam_paper(exam_paper_text)
      
        answer_key_text = self.document_reader.read_doc(answer_key) if isinstance(answer_key, bytes) else answer_key
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
                answer_paper_text = await asyncio.to_thread(self.document_reader.read_doc, answer_paper)
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
            failed_answer_papers.append(graded_answer_paper)