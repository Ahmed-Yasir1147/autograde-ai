from google import genai
from models.graded_paper_schemas import GradedPaper
from utils.helper_functions import inline_schema, singleton
from core.config import logger, GEMINI_STANDARD_MODEL_CODE
from utils.helper_functions import retry_gemini_requests
import json
from typing import List
from core.exceptions import IncorrectGradingError

@singleton
class ExamGrader:
    """A class to grade answer papers using the Gemini API according to given answer key and instructions."""

    def __init__(self, gemini_client: genai.Client):
            self.client = gemini_client

    def grade_exam_paper(
              self, 
              exam_paper_json: str, 
              answer_paper_json: str, 
              answer_key_json: str,
              instructions: str = "", 
              answer_paper_filename: str = ""
        ):
        """Grades an exam answer paper according to the given answer key and instructions using the Gemini API."""
        return retry_gemini_requests(
            lambda model_code: self._grade_exam_paper(exam_paper_json, answer_paper_json, answer_key_json, answer_paper_filename, instructions, model_code),
            answer_paper_filename
        )
    
    def _grade_exam_paper(
              self, 
              exam_paper_json: str, 
              answer_paper_json: str, 
              answer_key_json: str,
              answer_paper_filename: str = "",
              instructions: str = "",  
              model_code: str = GEMINI_STANDARD_MODEL_CODE
        ):
        logger.info(f"Grading exam paper: {answer_paper_filename}")
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
             model=model_code,
             input=prompt,
             response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": inline_schema(GradedPaper)
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
        # During validation, any error or false means failure in grading
        try:
            if self._validate_marks_range(graded_exam_dict, exam_paper_dict):
                return json.dumps(graded_exam_dict)
            else:
                raise IncorrectGradingError("Incorrect grading result from the model API.")
        except Exception as e:
            raise IncorrectGradingError(f"An error occurred while grading the exam: {e}")
            

    def _grade_objective(
              self, 
              exam_paper: dict, 
              answer_paper: dict, 
              graded_answer_paper: dict, 
              answer_key: dict
        ) -> dict:
        """Manually grades objective questions in the answer paper according to the answer key."""
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
        """Appends total marks obtained by objective and subjective questions in the answer paper."""
        total_marks = 0.0
        for question in graded_answer_paper["objective"]:        
                total_marks += question["marks_obtained"]
        for question in graded_answer_paper["subjective"]:
                total_marks += question["marks_obtained"] 
        graded_answer_paper["marks_obtained"] = total_marks
        return graded_answer_paper

    def _validate_marks_range(self, answer_paper_dict: dict, exam_paper_dict: dict) -> bool:
        """Validates if marks obtained by objective and subjective questions in the answer paper are within the range of marks in the exam paper."""
        graded_objective_questions = answer_paper_dict["objective"]
        graded_subjective_questions = answer_paper_dict["subjective"]
        objective_questions = exam_paper_dict["objective"]
        subjective_questions = exam_paper_dict["subjective"]

        if not self._in_range(answer_paper_dict["marks_obtained"], exam_paper_dict["marks"]):
            return False

        for i in range(len(graded_objective_questions)):
            if not self._in_range(graded_objective_questions[i]["marks_obtained"], objective_questions[i]["marks"]):
                return False

        return self._validate_nested_questions(graded_subjective_questions, subjective_questions)
            
            
    def _validate_nested_questions(self, graded_questions: List, exam_questions: List) -> bool:
        for i in range(len(graded_questions)):
            if not self._in_range(graded_questions[i]["marks_obtained"], exam_questions[i]["marks"]):
                return False

            graded_subquestions = graded_questions[i]["subquestions"]
            subquestions = exam_questions[i]["subquestions"]
            if subquestions is not None:
                if not self._validate_nested_questions(graded_subquestions, subquestions):
                    return False

        return True

    def _in_range(self, value: float, max: float, min: float = 0.0) -> bool:
        if value < min or value > max:
            return False
        else:
            return True




