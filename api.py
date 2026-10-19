import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from google import genai
from pydantic import BaseModel
from typing import Literal
from google.genai import types

load_dotenv()

# -----------------------------
# Gemini setup
# -----------------------------

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)

# -----------------------------
# MCQ schema
# -----------------------------

class MCQ(BaseModel):
    question_type: Literal["MCQ", "True/False"]
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_option: Literal["A", "B", "C", "D"]
    model_justification: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    


class MCQResponse(BaseModel):
    mcqs: list[MCQ]


# -----------------------------
# Flask app
# -----------------------------

app = Flask(__name__)


@app.route("/generate_mcqs", methods=["POST"])
def generate_mcqs():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "Request body is missing"
        }), 400

    notes_text = data.get("notes_text", "").strip()
    num_mcqs = data.get("num_mcqs", 5)
    topic_name = data.get("topic_name", "").strip()
    target_topic = data.get("target_topic", "").strip()
    generation_mode = data.get(
        "generation_mode",
        "pasted_notes"
    ).strip()

    question_type = data.get(
        "question_type",
        "MCQ"
    ).strip()

    if question_type not in ["MCQ", "True/False"]:
        question_type = "MCQ"

    difficulty = data.get(
        "difficulty",
        "Mixed"
    ).strip()

    if difficulty not in ["Easy", "Medium", "Hard", "Mixed"]:
        difficulty = "Mixed"


    # -----------------------------
    # Validate number of MCQs
    # -----------------------------

    try:
        num_mcqs = int(num_mcqs)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "error": "num_mcqs must be a number"
        }), 400

    if num_mcqs < 1 or num_mcqs > 30:
        return jsonify({
            "success": False,
            "error": "num_mcqs must be between 1 and 30"
        }), 400

    # -----------------------------
    # Validate input
    # -----------------------------

    if generation_mode != "topic_only" and not notes_text:
        return jsonify({
            "success": False,
            "error": "notes_text is required"
        }), 400

    # -----------------------------
    # Build prompt
    # -----------------------------

    if generation_mode == "topic_only":

        prompt = f"""
        Generate {num_mcqs} {question_type} questions.

Topic:
{topic_name}

Specific target topic:
{target_topic}

Requirements:
- Generate {num_mcqs} {question_type} questions.
- Questions must be based primarily on the provided study material.
- Do not introduce unrelated topics.
- Question type: {question_type}.
- Provide a short explanation for why the correct answer is correct.
- Requested difficulty: {difficulty}.
- If the requested difficulty is Easy, all questions must be Easy.
- If the requested difficulty is Medium, all questions must be Medium.
- If the requested difficulty is Hard, all questions must be Hard.
- If the requested difficulty is Mixed, distribute the questions across Easy, Medium, and Hard as evenly as possible.
- Avoid duplicate or nearly duplicate questions.
- Do not include the answer outside the structured fields.

- If the question type is True/False:
  - option_a must be "True".
  - option_b must be "False".
  - option_c must be an empty string.
  - option_d must be an empty string.
  - correct_option must be A for True or B for False.
  - The question must be a clear factual statement that can be answered only as True or False.

- If the question type is MCQ:
  - Provide exactly four meaningful options.
  - correct_option must be A, B, C, or D.
"""

    else:

        prompt = f"""
You are an AI assessment generator for an educational platform called Quentora.

Generate {num_mcqs} {question_type} questions from the study material below.

Topic:
{topic_name}

Specific target topic:
{target_topic}

Study material:
{notes_text}

Requirements:
- Generate exactly {num_mcqs} questions.
- Questions must be based primarily on the provided study material.
- Do not introduce unrelated topics.
- Question type: {question_type}.
- Provide a short explanation for why the correct answer is correct.
- Requested difficulty: {difficulty}.
- If the requested difficulty is Easy, all questions must be Easy.
- If the requested difficulty is Medium, all questions must be Medium.
- If the requested difficulty is Hard, all questions must be Hard.
- If the requested difficulty is Mixed, distribute the questions across Easy, Medium, and Hard as evenly as possible.
- Avoid duplicate or nearly duplicate questions.
- Do not include the answer outside the structured fields.


- If the question type is True/False:
  - option_a must be "True".
  - option_b must be "False".
  - option_c must be an empty string.
  - option_d must be an empty string.
  - correct_option must be A for True or B for False.
  - The question must be a clear factual statement that can be answered only as True or False.

- If the question type is MCQ:
  - Provide exactly four meaningful options.
  - correct_option must be A, B, C, or D.
"""

    # -----------------------------
    # Call Gemini with retry
    # -----------------------------

    import time

    models_to_try = [
        "gemini-3.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-3.6-flash",
        "gemini-3.7-flash"
    ]

    last_error = None

    try:

        for model_name in models_to_try:

            for attempt in range(3):

                try:
                    print(
                        f"Trying {model_name} "
                        f"(attempt {attempt + 1}/3)..."
                    )

                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_mime_type="application/json",
                            response_schema=MCQResponse,
                        ),
                    )

                    result = response.parsed

                    if not result:
                        raise ValueError(
                            "Gemini returned no structured MCQ data"
                        )

                    mcqs = [
                        mcq.model_dump()
                        for mcq in result.mcqs
                    ]

                    return jsonify({
                        "success": True,
                        "partial_success": len(mcqs) < num_mcqs,
                        "exact_success": len(mcqs) == num_mcqs,
                        "requested_count": num_mcqs,
                        "returned_count": len(mcqs),
                        "mcqs": mcqs,
                        "message": (
                            f"{len(mcqs)} {question_type} question(s) generated successfully."
                        ),
                        "model_used": model_name
                    })

                except Exception as e:

                    last_error = str(e)

                    print(
                        f"{model_name} failed: {last_error}"
                    )

                    # Retry only for temporary service errors
                    if "503" in last_error or "UNAVAILABLE" in last_error:

                        wait_time = 2 ** attempt

                        print(
                            f"Waiting {wait_time} seconds before retry..."
                        )

                        time.sleep(wait_time)

                    else:
                        break

        return jsonify({
            "success": False,
            "partial_success": False,
            "exact_success": False,
            "requested_count": num_mcqs,
            "returned_count": 0,
            "mcqs": [],
            "error": last_error or "Gemini generation failed"
        }), 500

    except Exception as e:

        return jsonify({
            "success": False,
            "partial_success": False,
            "exact_success": False,
            "requested_count": num_mcqs,
            "returned_count": 0,
            "mcqs": [],
            "error": str(e)
        }), 500
    



# -----------------------------
# Run server
# -----------------------------

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )