from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class GradedObjectiveAnswer(BaseModel):
    question_id: str = Field(description="Unique for objective question (same as in Question Paper)")
    marks_obtained: float = Field(description="Marks obtained => Range(0, total_marks)")
    reasoning: str = Field(description="""
        One (or few) word explanation of why you gave full or less marks like:
        Correct, Incorrect, etc
    """)

class GradedSubjectiveAnswer(BaseModel):
    question_id: str = Field(description="Unique for objective question (same as in Answer Paper)")
    marks_obtained: float = Field(description="""
        Marks obtained => Range(0, total_marks)
        Super question marks is sum of sub question marks (if there are any subquestions)
    """)
    reasoning: str = Field(description="""
        One (or few) word explanation of why you gave full or less marks like:
        Correct, Incorrect, Insufficient, Irrelevant, Too lengthy, Missing, etc.
    """)
    subquestions: Optional[List[GradedSubjectiveAnswer]] = Field(
        default=None, 
        description="""
        Nested list of subquestion evaluations for child parts (Q(n(m)), Q(n(m(o))), ...).
        This field MUST either contain child GradedSubjectiveAnswer objects OR be null/None. 
        """
    )

GradedSubjectiveAnswer.model_rebuild()

class GradedPaper(BaseModel):
    roll_no: str = Field(description="Roll number of student")
    name: str | None = Field(default=None, description="Name of student (if available)")
    objective: List[GradedObjectiveAnswer] | None = Field(default=None, description="Collectection of graded MCQs")
    subjective : List[GradedSubjectiveAnswer] | None = Field(default=None, description="Collection of graded answers of questions and subquestions")

GradedPaper.model_rebuild()

