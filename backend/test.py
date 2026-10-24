from services.grading_pipeline import GradingPipeline
from llama_cloud import LlamaCloud
from google import genai
from core.config import GEMINI_API_KEY
import pymupdf
import asyncio

llama_cloud = LlamaCloud()
gemini_client = genai.Client(api_key=GEMINI_API_KEY)
grading_pipeline = GradingPipeline(gemini_client, llama_cloud)

exam_paper = """
# GRADE 10 — COMPUTER SCIENCE
**Practice Examination**

**Time:** 60 minutes  
**Total Marks:** 30

Student Name: __________________________  
Roll Number: ___________________________

## General Instructions

1. Attempt all questions.
2. Section A contains 6 MCQs worth 1 mark each.
3. Section B contains subjective questions with subquestions.
4. Each subquestion carries the marks indicated beside it.
5. Subjective questions may be answered in any order, but clearly write the question and subquestion labels.
6. Show working where appropriate.
7. Unattempted questions receive zero marks.

## SECTION A — MULTIPLE-CHOICE QUESTIONS (6 Marks)

**Q1. Which component executes instructions in a computer? (1 mark)**

A. RAM  
B. CPU  
C. SSD  
D. Monitor

**Q2. Which of the following is volatile memory? (1 mark)**

A. ROM  
B. SSD  
C. RAM  
D. DVD

**Q3. In Python, which symbol begins a single-line comment? (1 mark)**

A. `//`  
B. `<!--`  
C. `#`  
D. `**`

**Q4. What is the decimal value of binary `1010`? (1 mark)**

A. 8  
B. 10  
C. 12  
D. 14

**Q5. Which data structure follows FIFO order? (1 mark)**

A. Stack  
B. Queue  
C. Tree  
D. Graph

**Q6. Which protocol is commonly used to load web pages securely? (1 mark)**

A. FTP  
B. HTTP only  
C. HTTPS  
D. SMTP

## SECTION B — SUBJECTIVE QUESTIONS (24 Marks)

### Q7. Computer Fundamentals (6 marks)

**(a)** State one difference between RAM and ROM. (2 marks)

**(b)** Explain one reason why a computer needs secondary storage. (2 marks)

**(c)** Name one input device and one output device. (2 marks)

### Q8. Programming Basics (6 marks)

**(a)** What is a variable in programming? (2 marks)

**(b)** Write a Python expression that calculates the remainder when 17 is divided by 5. (2 marks)

**(c)** What is the output of the following code? (2 marks)

```python
x = 3
print(x * 2 + 1)
```

### Q9. Algorithms and Data Structures (6 marks)

**(a)** Define an algorithm. (2 marks)

**(b)** Give one difference between a stack and a queue. (2 marks)

**(c)** A Python list contains `[4, 7, 9]`. What is the index of value `7`? (2 marks)

### Q10. Networks and Security (6 marks)

**(a)** What is the purpose of an IP address? (2 marks)

**(b)** Give one difference between HTTP and HTTPS. (2 marks)

**(c)** State one good practice for creating a strong password. (2 marks)

**END OF EXAM PAPER**"""
answer_paper_1 = """
# STUDENT ANSWER PAPER

**Student Name:** Student A  
**Roll Number:** 1042  
**Subject:** Computer Science

## SECTION A — MCQs

Q1. B  
Q2. C  
Q3. C  
Q4. B  
Q5. A  
Q6. C

## SECTION B — SUBJECTIVE ANSWERS

### Q7

**(a)** RAM loses its data when power is off, but ROM keeps its data.

**(b)** Secondary storage keeps files even when the computer is switched off.

**(c)** Input device: Keyboard. Output device: Monitor.

### Q8

**(a)** A variable is a named place used to store a value.

**(b)** `17 % 5`

**(c)** The output is `7`.

### Q9

**(a)** An algorithm is a step-by-step method for solving a problem.

**(b)** A stack is LIFO, while a queue is FIFO.

**(c)** `1`

### Q10

**(a)** An IP address identifies a device on a network.

**(b)** HTTPS encrypts communication, while HTTP does not provide the same transport encryption.

**(c)**

[Left blank by the student.]

**END OF ANSWER PAPER**"""
answer_paper_2 = """
# STUDENT ANSWER PAPER

**Student Name:** Student B  
**Roll Number:** 1079  
**Subject:** Computer Science

## SECTION A — MCQs

Q1. B  
Q2. A  
Q3. C  
Q4. B  
Q5. B  
Q6. C

## SECTION B — SUBJECTIVE ANSWERS

### Q10

**(c)** Use a long password with a mix of letters, numbers, and symbols.

**(a)** It is an address that helps identify a device on a network.

**(b)** HTTPS encrypts data sent between the browser and the website.

### Q8

**(c)** It prints `7`.

**(a)** A variable stores a value under a name.

**(b)** [Not attempted]

### Q7

**(c)** Keyboard is an input device; speakers are output devices.

**(a)** RAM is temporary, and ROM is permanent.

**(b)** It saves data for later use even without power.

### Q9

**(b)** A stack removes the last item added, while a queue removes the first item added.

**(a)** A finite series of clear steps to solve a task.

**(c)** [Not attempted]

**END OF ANSWER PAPER**"""
answer_paper_3 = pymupdf.open("notebooks/test_documents/handwritten_exam_3.pdf").tobytes()
answer_paper_4 = pymupdf.open("notebooks/test_documents/handwritten_exam_4.pdf").tobytes()

answer_key = """
# OPTIONAL ANSWER KEY AND MARKING RUBRIC

## Section A — MCQ Answer Key (6 marks)

| Question | Correct Answer | Marks |
|---|---|---:|
| Q1 | B — CPU | 1 |
| Q2 | C — RAM | 1 |
| Q3 | C — # | 1 |
| Q4 | B — 10 | 1 |
| Q5 | B — Queue | 1 |
| Q6 | C — HTTPS | 1 |

Award 1 mark for a correct answer and 0 for an incorrect, ambiguous, or blank answer.

## Section B — Subjective Marking Scheme (24 marks)

### Q7. Computer Fundamentals

**(a) RAM vs ROM — 2 marks**
- RAM is volatile or loses contents when power is removed: 1 mark.
- ROM is non-volatile or retains contents without power: 1 mark.

**(b) Secondary storage — 2 marks**
- Explains that secondary storage retains files or data when power is off: 2 marks.
- Award 1 mark for a partially correct explanation.

**(c) Input and output devices — 2 marks**
- One valid input device: 1 mark.
- One valid output device: 1 mark.

Examples: keyboard, mouse, scanner, monitor, speakers, printer.

### Q8. Programming Basics

**(a) Variable — 2 marks**
- Explains that a variable is a named identifier or location used to store or refer to a value: 2 marks.
- A partial answer such as “stores a value”: 1 mark.

**(b) Remainder expression — 2 marks**
- `17 % 5`: 2 marks.
- Another valid Python expression that calculates the same remainder: 2 marks.

**(c) Code output — 2 marks**
- Correct output: `7`: 2 marks.

### Q9. Algorithms and Data Structures

**(a) Algorithm — 2 marks**
- Describes a finite or ordered set of clear steps for solving a problem: 2 marks.
- Partially correct definition: 1 mark.

**(b) Stack vs queue — 2 marks**
- Stack follows LIFO: 1 mark.
- Queue follows FIFO: 1 mark.

**(c) Python list index — 2 marks**
- Correct answer: `1`: 2 marks.
- Python uses zero-based indexing.

### Q10. Networks and Security

**(a) IP address — 2 marks**
- Explains that an IP address identifies or addresses a device/interface on a network: up to 2 marks.
- Partial explanation of network identification: 1 mark.

**(b) HTTP vs HTTPS — 2 marks**
- HTTPS uses TLS encryption to protect communication: 1 mark.
- HTTP does not provide the same TLS-protected communication: 1 mark.

**(c) Strong password — 2 marks**
Award up to 2 marks for a valid security practice, such as:
- Using a long, unique password.
- Using a password manager to generate unique passwords.
- Avoiding predictable personal information.
- Using a combination of character types.

Award 1 mark for a relevant but incomplete answer.

## General Marking Rules

1. Award partial credit when the student demonstrates some correct understanding.
2. Accept semantically equivalent wording.
3. Do not require exact memorization of the answer key.
4. Do not penalize grammar or spelling unless the intended meaning is unclear.
5. A blank or explicitly unattempted subquestion receives zero.
6. Never award more than the maximum marks for a subquestion.
7. Calculate each question subtotal and section subtotal independently.
8. The maximum overall score is 30 marks.

## Expected Totals Structure

- Section A: 6 marks maximum.
- Section B: 24 marks maximum.
- Overall: 30 marks maximum.
 
"""

instructions = """
# AUTOGRADE AI — GRADING INSTRUCTIONS

You are grading Grade 10 Computer Science examination answer papers.

## Input Files

1. The original exam paper.
2. One or more student answer papers.
3. An optional teacher-provided answer key and marking rubric.

## Grading Procedure

### Step 1 — Parse the Exam Paper

Extract:
- Subject and exam details.
- Each question number.
- Each subquestion label.
- Maximum marks for every question and subquestion.
- Question type: objective or subjective.
- Section totals and overall maximum marks.

The expected overall maximum is 30 marks.

### Step 2 — Parse Each Student Paper

Extract the student name and roll number when available.

Associate each answer with its question and subquestion labels. Answers may appear in a different order from the exam paper.

Do not associate answers based only on their position in the document.

### Step 3 — Grade Objective Questions

Section A contains six MCQs, each worth one mark.

If an answer key is provided:
- Compare the student's selected option with the correct option.
- Award 1 mark for a correct option.
- Award 0 marks for an incorrect, ambiguous, or blank answer.

If no answer key is provided:
- Infer the correct answer from the question and standard subject knowledge.
- Flag uncertain cases for review.

### Step 4 — Grade Subjective Questions

Grade each subquestion independently.

Use the maximum marks printed on the exam and the optional marking rubric if supplied.

Award partial credit for correct concepts, reasoning, and equivalent wording.

Do not require exact wording from the answer key.

### Step 5 — Handle Missing Answers

A blank or explicitly unattempted subquestion must receive zero marks.

Do not:
- Invent an answer.
- Shift subsequent answers into a blank subquestion.
- Treat an omitted answer as an answer to the next question.
- Confuse missing answers with OCR failures.

If the answer may have been missed because of unclear extraction or OCR, add a review flag rather than silently guessing.

### Step 6 — Handle Different Answer Orders

Subjective questions may be answered in any order.

For example, Student B answers Q10 before Q8, Q7, and Q9. This is intentional.

Match answers using the question and subquestion labels, not the order in which they appear.

### Step 7 — Calculate Marks

For every subquestion, record:
- Question number.
- Subquestion label.
- Detected student answer.
- Maximum marks.
- Marks awarded.
- Brief grading explanation.

Then calculate:
- Each question's subtotal.
- Section A subtotal.
- Section B subtotal.
- Overall score out of 30.

Check that no score exceeds its maximum.

### Step 8 — Return Structured Output

Prefer valid JSON with a structure similar to this:

{
  "student_name": "Student A",
  "roll_number": "1042",
  "section_totals": {
    "objective": {
      "awarded": 0,
      "maximum": 6
    },
    "subjective": {
      "awarded": 0,
      "maximum": 24
    }
  },
  "questions": [
    {
      "question_number": "Q7",
      "subquestions": [
        {
          "label": "a",
          "detected_answer": "Student's extracted answer",
          "marks_awarded": 0,
          "max_marks": 2,
          "reason": "Brief explanation"
        }
      ],
      "awarded": 0,
      "maximum": 6
    }
  ],
  "total_marks": 0,
  "maximum_marks": 30,
  "unattempted_parts": [],
  "review_flags": []
}

The numeric scores above are placeholders illustrating the schema, not actual grades.

Ensure the final JSON is syntactically valid and contains no explanatory prose outside the JSON if JSON-only output is requested.

## Validation Checks

Student A:
- MCQs Q1, Q2, Q3, Q4, and Q6 are correct.
- MCQ Q5 is incorrect.
- Q10(c) is blank and must receive zero.

Student B:
- MCQs Q1, Q3, Q4, Q5, and Q6 are correct.
- MCQ Q2 is incorrect.
- Subjective answers appear in a scrambled order.
- Q8(b) and Q9(c) are unattempted and must each receive zero.

For both students:
- Every answer must be mapped to the correct question.
- No subquestion may exceed its maximum marks.
- The final total must not exceed 30.
- Missing answers must remain missing and receive zero.
- Subjective partial-credit decisions should be explainable.

## Testing Modes

**Blind grading:** Provide the exam and student papers only. Do not provide the optional answer key.

**Key-assisted grading:** Provide the exam, student papers, and answer key as a separate teacher reference.

Compare structural accuracy separately from subjective grading quality.

Structural accuracy includes correct question mapping, missing-answer detection, mark ceilings, section totals, and overall totals.
"""

grading_response = asyncio.run(grading_pipeline.grade_exams(
    exam_paper,
    {"answer_paper_1": answer_paper_1, "answer_paper_2": answer_paper_2, "answer_paper_3": answer_paper_3},
    answer_key,
    instructions
))

print(grading_response.model_dump_json())

