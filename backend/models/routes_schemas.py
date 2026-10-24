from pydantic import BaseModel, Field
from typing import List, Dict

class GradingRequest(BaseModel):
    exam_paper: bytes | str = Field(description="The exam paper to be graded either as a file or as a string.")
    answer_papers: Dict[str, bytes | str] = Field(description="A dictionary of answer papers, where the key is the filename and the value is a list of answer papers either as files or strings.")
    answer_key: bytes | str = Field(description="The answer key to be used for grading either as a file or as a string.")
    instructions: str = Field(description="The grading instructions to be used for grading.")
    grading_scheme: str = Field(description="The grading scheme to be used for grading.")
    concurrency: int = Field(default=3, description="The number of concurrent tasks to be used for grading.")

class GradingResponse(BaseModel):
    total_papers: int = Field(description="The total number of answer papers graded.")
    successful_papers: int = Field(description="The number of answer papers graded successfully.")
    failed_papers: int = Field(description="The number of answer papers graded unsuccessfully.")
    total_marks: float = Field(description="The total marks awarded for the exam.")
    average_marks: float = Field(description="The average marks awarded for the exam.")
    minimum_marks: float = Field(description="The minimum marks awarded for the exam.")
    maximum_marks: float = Field(description="The maximum marks awarded for the exam.")
    graded_answer_papers: List[str] = Field(description="A list of graded answer papers.")
    failed_answer_papers: List[str] = Field(description="A list of graded answer papers which failed validation.")