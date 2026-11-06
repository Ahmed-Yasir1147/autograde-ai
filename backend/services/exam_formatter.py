from google import genai
from models.formatted_paper_schemas import ExamPaper, AnswerPaper
from utils.helper_functions import inline_schema, singleton
from core.config import logger, GEMINI_STANDARD_MODEL_CODE
from core.exceptions import IncorrectFormattingError
from utils.helper_functions import retry_gemini_requests
import json
from typing import List

@singleton
class ExamFormatter:
    """A class to format exam and answer papers using the Gemini API."""

    def __init__(self, client: genai.Client):
        self.client = client

    def format_exam_paper(self, exam_paper: str) -> str:
        logger.info("Formatting exam paper")
        """Formats an exam paper according to the specified schema using the Gemini API."""
        return retry_gemini_requests(
            lambda model_code: self._format_exam_paper(exam_paper, model_code),
            "exam_paper"
        )

    def _format_exam_paper(self, exam_paper: str, model_code: str = GEMINI_STANDARD_MODEL_CODE):
        response = self.client.interactions.create(
            model=model_code,
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
                # build explicit schema because nested subquestions due to recursive schema is lost otherwise
                "schema": inline_schema(ExamPaper)
            },
        )
        formatted_exam_paper = ExamPaper.model_validate_json(response.output_text)
        formatted_exam_paper = self._set_marks(formatted_exam_paper.model_dump_json())
        logger.info(f"Exam paper {formatted_exam_paper}")
        return formatted_exam_paper
    
    def format_answer_paper(self, answer_paper: str, exam_paper: str, answer_paper_filename: str = "") -> str:   
        logger.info(f"Formatting answer paper: {answer_paper_filename}")
        """Formats an answer paper according to the specified schema using the Gemini API."""
        return retry_gemini_requests(
            lambda model_code: self._format_answer_paper(answer_paper, exam_paper, model_code),
            answer_paper_filename
        )

    def _format_answer_paper(self, answer_paper: str, exam_paper: str, model: str = GEMINI_STANDARD_MODEL_CODE):
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
                "schema": inline_schema(AnswerPaper, "subanswers")
            },
        )
        formatted_answer_paper = AnswerPaper.model_validate_json(response.output_text)
        if not self._validate_answer_paper(formatted_answer_paper.model_dump_json(), exam_paper):
            raise IncorrectFormattingError("Incorrectly formatted answer paper.")
        return formatted_answer_paper.model_dump_json()

    def format_answer_key(self, answer_key: str, exam_paper: str) -> str:
        """Formats an answer key according to the specified schema using the Gemini API."""
        return retry_gemini_requests(
            lambda model_code: self._format_answer_key(answer_key, exam_paper, model_code),
            "answer_key"
        )

    def _format_answer_key(self, answer_key: str, exam_paper: str, model: str = GEMINI_STANDARD_MODEL_CODE):
        logger.info("Formatting answer key")
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
                "schema": inline_schema(AnswerPaper, "subanswers")
            },
        )
        formatted_answer_key = AnswerPaper.model_validate_json(response.output_text)
        return formatted_answer_key.model_dump_json()

    def _set_marks(self, exam_paper: str) -> str:
        """Sets the marks for the paper and each superquestion."""
        exam_paper_dict = json.loads(exam_paper)

        if exam_paper_dict.get("subjective"):
            self._set_question_marks(exam_paper_dict["subjective"])

        exam_paper_dict = self._set_total_marks(exam_paper_dict)

        return json.dumps(exam_paper_dict)


    def _set_question_marks(self, questions: list) -> int:
        total_marks = 0

        for question in questions:
            if question.get("subquestions"):
                question["marks"] = self._set_question_marks(
                    question["subquestions"]
                )
            else:
                question["marks"] = question.get("marks", 0)

            total_marks += question["marks"]

        return total_marks


    def _set_total_marks(self, exam_paper_dict: dict):
        total_marks = 0

        for question in exam_paper_dict.get("objective", []):
            total_marks += question.get("marks", 0)

        for question in exam_paper_dict.get("subjective", []):
            total_marks += question.get("marks", 0)

        exam_paper_dict["marks"] = total_marks

        return exam_paper_dict
        
    def _validate_answer_paper(self, answer_paper: str, exam_paper: str) -> bool:
        """Validates if answer paper has same number, order and hierarchy of questions as the exam paper."""
        answer_paper_dict = json.loads(answer_paper)
        exam_paper_dict = json.loads(exam_paper)
        if exam_paper_dict["objective"]:
            if not answer_paper_dict["objective"]:
                return false
            for i in range(len(answer_paper_dict["objective"])):
                if answer_paper_dict["objective"][i]["question_id"] != exam_paper_dict["objective"][i]["question_id"]:
                    return False
        if exam_paper_dict["subjective"]:
            if not answer_paper_dict["subjective"]:
                return false
            return self._validate_subjective_answers(
                answer_paper_dict["subjective"], 
                exam_paper_dict["subjective"]
            )
        else:
            return True

    def _validate_subjective_answers(self, answer_paper_questions: List, exam_paper_questions: List) -> bool:
        for i in range(len(answer_paper_questions)):
            if answer_paper_questions[i]["question_id"] != exam_paper_questions[i]["question_id"]:
                return False
            if exam_paper_questions[i]["subquestions"] is not None:
                if not self._validate_subjective_answers(answer_paper_questions[i]["subanswers"], exam_paper_questions[i]["subquestions"]):
                    return False
        return True

    
    


    
