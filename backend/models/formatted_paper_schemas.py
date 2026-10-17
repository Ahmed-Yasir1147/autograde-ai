from __future__ import annotations
from pydantic import BaseModel, Field
from typing import List, Optional

class SubjectiveQuestion(BaseModel):
    question_id: str = Field(description="""
        Unique id for question in this format: 
        Q(n) where n is question number
        Q(n(m)) where n is parent question number while m is subquestion number
        and so on...
    """)
    marks: float = Field(description="Marks of the question or sum of marks of inner questions")
    question_statement: str = Field(description="""
        Statement or description the of the question. 
        It must not include sub questions statement (which will become part of "subquestions")
    """)
    subquestions: Optional[List[SubjectiveQuestion]] = Field(
        default=None, 
        description=""" 
        List of subquestions (Q(n(m)), Q(n(m(o))), ...) belonging directly to this question. 
        This field either has subquestions or is null/None (never empty list [])
        """
    )

SubjectiveQuestion.model_rebuild()

class ObjectiveQuestion(BaseModel):
    question_id: str = Field(description="""
        Unique id for question in this format: 
        Q(n) where n is question number
        Q(n(m)) where n is outer question number while m is inner question number
        and so on...
        """)
    marks: float = Field(description="Mark of the MCQ")
    mcq_statement: str = Field(description="Statement MCQ and its options")

class ExamPaper(BaseModel):
    subject : str = Field(description="Name of the subject")
    course_id: str | None = Field(default=None, description="ID of paper (only if available)")
    date: str | None = Field(default=None, description="Date of exam (only if available)")
    marks: float = Field(description="Total marks of all questions in the exam")
    objective: List[ObjectiveQuestion] | None = Field(default=None, description="Collection of Objective MCQs")
    subjective: List[SubjectiveQuestion] | None = Field(default=None, description="Collection of questions and sub questions")

ExamPaper.model_rebuild()

class ObjectiveAnswer(BaseModel):
    question_id: str = Field(description="""
        Unique id for question in this format Q(n) or Q(n(m)) or...
        Extract it from reference Exam paper
        """)
    chosen_option: str = Field(description="The identifier of option chosen for MCQ. If student selected more than one student, give ''.")

class SubjectiveAnswer(BaseModel):
    question_id: str = Field(description="""
        Unique id forq uestion in this format Q(n) or Q(n(m)) or...
        Extract it from reference Exam paper
    """)
    answer_statement: str | None = Field(default=None, description="Statement or text of the answer (A question will either have answer statement or sub answers)")
    subanswers: Optional[List[SubjectiveAnswer]] = Field(
        default=None, 
        description="""
            List of subanswers (Q(n(m)), Q(n(m(o))), ...) belonging directly to this question. 
            This field either has subquestions or is null/None (never empty list [])
            A question will either have answer statement or sub answers 
        """
    )

SubjectiveAnswer.model_rebuild()

class AnswerPaper(BaseModel):
    subject : str = Field(description="Name of the subject")
    roll_no: str = Field(description="Roll number of student")
    name: str | None = Field(default=None, description="Name of student (if available)")
    objective: List[ObjectiveAnswer] | None = Field(default=None, description="Collectection of MCQ chosen options")
    subjective : List[SubjectiveAnswer] | None = Field(default=None, description="Collection of answers and sub answers")

AnswerPaper.model_rebuild()