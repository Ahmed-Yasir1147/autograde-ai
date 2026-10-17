# Dumping various pipeline components for easy importing in pipeline.ipynb 

from __future__ import annotations
from llama_cloud import LlamaCloud
from pydantic import BaseModel, Field
from typing import List, Optional
from google import genai
import copy
import json

# DOCUMENT READER

class DocumentReader:

    def __init__(self, llama_cloud: LlamaCloud):
        self.client = llama_cloud

    def read_doc(self, file_bytes: bytes):
        file = self.client.files.create(file=file_bytes, purpose="parse")
        result = self.client.parsing.parse(
            file_id=file.id,
            tier="cost_effective",
            version="latest",
            expand=["markdown"],
        )
        text = ""
        for page in result.markdown.pages:
            text += page.markdown
        return text

# EXAM FORMATTER

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

class ExamFormatterGemini:

    def __init__(self, client: genai.Client):
        self.client = client

    def format_exam_paper(self, exam_paper: str, model: str = "gemini-3.5-flash-lite"):
        response = self.client.interactions.create(
            model=model,
            input=f"""
                Format this exam according to given schema. 
                Carefully identify questions and their subquestions. 
                If a question contains sub-parts or sub-questions, you MUST populate the "subquestions" list with nested SubjectiveQuestion objects. 
                Do not leave subquestions empty or null if sub-parts are present in the text.
                You will encounter marks of question in front of them.
                Exam paper: {exam_paper}
                Ignore markdown tags, escape sequences & special symbols while not losing any question.
            """,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": self.__inline_schema(ExamPaper)
            },
        )
        formatted_exam_paper = ExamPaper.model_validate_json(response.output_text)
        return formatted_exam_paper.model_dump_json()

    def format_answer_paper(self, answer_paper: str, exam_paper: str, model: str = "gemini-3.5-flash-lite"):
        response = self.client.interactions.create(
            model=model,
            input=f"""
                Format this answer paper according to given schema. 
                Carefully identify answers and their subanswers and format subanswer as part of "answers" of super answer.
                Exam paper is also attached so that you strictly follow the question ids and structure. The answer paper should have
                answers for all the questions & subquestions present in exam paper with same order and hierarchy even if empty.
                Exam paper: {exam_paper}
                Answer paper: {answer_paper}
                Ignore markdown tags, escape sequences & special symbols while not losing any question & its answer.
            """,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": self.__inline_schema(AnswerPaper, "subanswers")
            },
        )
        formatted_answer_paper = AnswerPaper.model_validate_json(response.output_text)
        return formatted_answer_paper.model_dump_json()

    def format_answer_key(self, answer_key: str, exam_paper: str, model: str = "gemini-3.5-flash-lite"):
        response = self.client.interactions.create(
            model=model,
            input=f"""
                Format this answer key according to given schema. 
                Carefully identify answers and their subanswers and format subanswer as part of "answers" of super answer.
                Exam paper is also attached so that you strictly follow the question ids and structure. The answer key should have
                answers for all the questions & subquestions present in exam paper with same order and hierarchy even if empty.
                Roll number and name of student can be ANSWER_KEY.
                Exam paper: {exam_paper}
                Answer key: {answer_key}
                Ignore markdown tags, escape sequences & special symbols while not losing any objective or subjective question & its answer.
            """,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": self.__inline_schema(AnswerPaper, "subanswers")
            },
        )
        formatted_answer_key = AnswerPaper.model_validate_json(response.output_text)
        return formatted_answer_key.model_dump_json()

    def __inline_schema(self, model, property_name="subquestions", depth=4):
        schema = model.model_json_schema()
        defs = schema.pop("$defs", {})

        def resolve(node, d):
            if isinstance(node, dict):
                if "$ref" in node:
                    target = copy.deepcopy(defs[node["$ref"].split("/")[-1]])
                    if d <= 1:  # last level: no further nesting
                        target.get("properties", {}).pop(property_name, None)
                    return resolve(target, d - 1)
                return {k: resolve(v, d) for k, v in node.items()}
            if isinstance(node, list):
                return [resolve(i, d) for i in node]
            return node

        return resolve(schema, depth)


# EXAM GRADER
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
class ExamGrader:
    def __init__(self, gemini_client: genai.Client):
            self.client = gemini_client
    
    def grade_exam_paper(self, exam_paper_json: str, answer_paper_json: str, answer_key_json: str,instructions: str = "",  model: str = "gemini-3.5-flash-lite"):
        prompt = f"""
            You have to grade an exam answer paper and return response in desired format.
            Exam paper: {exam_paper_json}
            Answer paper: {answer_paper_json}
            Instructions : {instructions}
            CRITICAL RULES:
            1. STRICT MATCHING: Map answers directly to the corresponding question IDs from the Exam Paper.
            2. PRESERVE HIERARCHY: If in Exam Paper/ Anwer Paper, there is nesting of subquestions, same should be reflected in Graded Exam Paper.
            3. MARKS AGGREGATION: The `marks_obtained` for a parent question MUST equal the sum of `marks_obtained` across all its inner `subquestions`.
            4. INSTRUCTIONS: Follow (if any) strictly. Don't be too generous or strict unless explicitly asked.
            5. ANSWER KEY: If user provides answer key, follow correct MCQ answers strictly while subjective answers as per instructions. 
        """
        response = self.client.interactions.create(
             model=model,
             input=prompt,
             response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": self.inline_schema(GradedPaper)
             },
        )
        formatted_graded_exam = GradedPaper.model_validate_json(response.output_text)
        exam_paper_dict = json.loads(exam_paper_json)
        answer_paper_dict = json.loads(answer_paper_json)
        graded_exam_dict = json.loads(formatted_graded_exam.model_dump_json())
        answer_key_dict = json.loads(answer_key_json)
        # If answer key is provided, grade objective questions are rechecked against it
        if graded_exam_dict["objective"] and answer_key_dict:
            graded_exam_dict = self._grade_objective(exam_paper_dict, answer_paper_dict, graded_exam_dict, answer_key_dict)
        graded_exam_dict = self._append_total_marks(graded_exam_dict)
        return json.dumps(graded_exam_dict)

    def inline_schema(self, model, property_name="subquestions", depth=4):
        schema = model.model_json_schema()
        defs = schema.pop("$defs", {})

        def resolve(node, d):
            if isinstance(node, dict):
                if "$ref" in node:
                    target = copy.deepcopy(defs[node["$ref"].split("/")[-1]])
                    if d <= 1:  
                        target.get("properties", {}).pop(property_name, None)
                    return resolve(target, d - 1)
                return {k: resolve(v, d) for k, v in node.items()}
            if isinstance(node, list):
                return [resolve(i, d) for i in node]
            return node

        return resolve(schema, depth)

    def _grade_objective(self, exam_paper: dict, answer_paper: dict, graded_answer_paper: dict, answer_key: dict) -> dict:
        objective_questions = exam_paper["objective"]
        objective_answers = answer_paper["objective"]
        graded_objective_answers = graded_answer_paper["objective"]
        objective_answer_key = answer_key["objective"]
        for i in range(len(graded_objective_answers)):
            if objective_answers[i]["chosen_option"].lower() == objective_answer_key[i]["chosen_option"].lower():
                graded_objective_answers[i]["marks_obtained"] = objective_questions[i]["marks"]
                graded_objective_answers[i]["reasoning"] = "Correct"
            else:
                graded_objective_answers[i]["marks_obtained"] = 0.0
                graded_objective_answers[i]["reasoning"] = "Incorrect"
        return graded_answer_paper

    def _append_total_marks(self, graded_answer_paper: dict) -> dict:
        total_marks = 0.0
        for question in graded_answer_paper["objective"]:        
                total_marks += question["marks_obtained"]
        for question in graded_answer_paper["subjective"]:
                total_marks += question["marks_obtained"] 
        graded_answer_paper["marks_obtained"] = total_marks
        return graded_answer_paper


