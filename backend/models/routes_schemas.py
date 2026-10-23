from pydantic import BaseModel, Field
from typing import List, Dict

class GradingRequest(BaseModel):
    exam_paper: bytes | str = Field(description="The exam paper to be graded either as a file or as a string.")
    answer_papers: Dict[str, bytes | str] = Field(description="A dictionary of answer papers, where the key is the filename and the value is a list of answer papers either as files or strings.")
    answer_key: bytes | str = Field(description="The answer key to be used for grading either as a file or as a string.")
    instructions: str = Field(description="The grading instructions to be used for grading.")
    concurrency: int = Field(default=3, description="The number of concurrent tasks to be used for grading.")

class GradingResponse(BaseModel):
    graded_answer_papers: List[str] = Field(description="A list of graded answer papers.")
    failed_answer_papers: List[str] = Field(description="A list of graded answer papers which failed validation.")