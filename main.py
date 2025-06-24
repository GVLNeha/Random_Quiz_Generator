import enum
import json
import os
import re
from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
from typing import Dict,List

from starlette.responses import JSONResponse

app = FastAPI()
client = OpenAI()

class Diff(str,enum.Enum):
    easy="easy"
    medium="medium"
    hard="hard"

class Quiz(BaseModel):
    topic: str
    num_questions: int | None = 5
    difficulty: Diff | None = Diff.medium

class Question(BaseModel):
    question: str
    options: Dict[str, str]
    answer: str
    explanation: str | None = None

class QuizOut(BaseModel):
    topic: str
    questions: List[Question]


@app.post("/generate-quiz/", response_model=QuizOut)
def generate_quiz(quiz: Quiz):
    if not quiz.topic.strip():
        return JSONResponse(status_code=400, content={"error": "Topic cannot be empty."})

    if len(quiz.topic.strip()) > 100:
        return JSONResponse(status_code=400, content={"error": "Topic must be 100 characters or fewer."})

    if quiz.num_questions <= 0 or quiz.num_questions > 20:
        return JSONResponse(
            status_code=400,
            content={"error": "Number of questions must be between 1 and 20."}
        )
    prompt=f"""
Generate a {quiz.difficulty} quiz on the topic "{quiz.topic}" with {quiz.num_questions} multiple choice questions.
Only generate questions if the topic is a real, known subject.
If it's invalid or not specific enough, respond with:
"Sorry, I cannot generate questions on that topic."
Each question should contain:
- question text
- 4 options (A-D)
- the correct answer
- an explanation

Respond in this exact JSON format:

{{
  "topic": "{quiz.topic}",
  "questions": [
    {{
      "question": "string",
      "options": {{
        "A": "string",
        "B": "string",
        "C": "string",
        "D": "string"
      }},
      "answer": "A",
      "explanation": "string"
    }}
  ]
}}

Only return valid JSON. No extra text.
"""
    try:
        completion=client.chat.completions.create(
            model="gpt-4o",
            messages = [
                dict(role="system", content="You are quiz generator bot"),
                dict(role="user", content=prompt)
            ]
        )
        content=completion.choices[0].message.content
       # print("OpenAI raw response:", content)
        cleaned = re.sub(r"```json|```", "", content).strip()
        quiz_json =json.loads(cleaned)
        validated_quiz = QuizOut(**quiz_json)
        if not validated_quiz.questions:
            return JSONResponse(
                status_code=400,
                content={"error": "Could not generate questions. Please enter a more specific or valid topic."}
            )
        else:
            return validated_quiz
    except Exception as e:
        return JSONResponse(status_code=500, content={"error":str(e)})
