# AutoGrade AI

An AI-powered automated exam grading system that evaluates handwritten student exam papers and generates structured grading reports.

## Problem Statement

Manual exam grading is time-consuming, repetitive, and prone to inconsistencies. AutoGrade AI aims to simplify this process by automating handwritten answer extraction, answer evaluation, and marks calculation using OCR and large language models.

## Tech Stack

- **Backend:** FastAPI
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **Containerization:** Docker
- **OCR:** LlamaIndex OCR integration
- **Formatting & Grading:** Google Gemini API

## Processing Pipeline

`Upload → OCR → Formatting → Grading → Marks & Grades`

1. **Upload:** Submit an exam paper, handwritten student papers with optional answer keys and instructions.
2. **OCR:** Extract handwritten and printed text from uploaded documents.
3. **Formatting:** Structure extracted content into an organized question-and-answer format.
4. **Grading:** Evaluate student responses using Gemini API and the configured grading scheme.
5. **Results:** Calculate marks and grades and generate downloadable reports.

## Features

- **Handwritten Exam Grading:** Automatically evaluates handwritten student answer sheets.
- **Bubble Sheet Checking:** Supports automated checking of objective bubble-sheet responses.
- **Custom Grading Schemes:** Allows configuration of grading scheme.
- **Downloadable Reports:** Export grading results in PDF and CSV formats.

## Limitations

- English-language papers only.
- Optional questions are not supported.
- Diagrams and shapes are not supported.
- Objective questions are currently limited to MCQs.
- Relies on external APIs, with usage subject to their free-tier quotas and limitations.

## Deployment
- **Frontend** Vercel
- **Backend** Render

**[Access AutoGrade AI](YOUR_DEPLOYMENT_URL)**
