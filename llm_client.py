
import os
import json
import re
import requests

# Primary Gemini model
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash").strip()

# Fallback models are tried automatically if the previous model fails.
# You can override this list using GEMINI_FALLBACK_MODELS in Vercel.
DEFAULT_FALLBACK_MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
]

_env_fallback_models = os.getenv("GEMINI_FALLBACK_MODELS", "").strip()

if _env_fallback_models:
    FALLBACK_MODELS = [
        model.strip()
        for model in _env_fallback_models.split(",")
        if model.strip()
    ]
else:
    FALLBACK_MODELS = DEFAULT_FALLBACK_MODELS


def _gemini(prompt, timeout=90, models=None):
    """
    Call Gemini using a sequence of models.
    If one model fails, try the next model automatically.
    """

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY environment variable is missing."
        )

    # Try the configured primary model first, then the fallback models.
    model_candidates = models or [
    GEMINI_MODEL,
    *DEFAULT_FALLBACK_MODELS
]

    # Remove duplicates while preserving the order.
    model_candidates = list(dict.fromkeys(model_candidates))

    errors = []

    for model in model_candidates:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/"
            f"models/{model}:generateContent"
        )

        try:
            print(f"Trying Gemini model: {model}")

            response = requests.post(
                url,
                headers={
                    "x-goog-api-key": GEMINI_API_KEY,
                    "Content-Type": "application/json",
                },
                json={
                    "contents": [
                        {"parts": [{"text": prompt}]}
                    ],
                    "generationConfig": {
                        "temperature": 0.2,
                        "maxOutputTokens": 8192,
                        "responseMimeType": "application/json",
                    },
                },
                timeout=timeout,
            )

            if response.status_code != 200:
                try:
                    error_message = (
                        response.json()
                        .get("error", {})
                        .get("message", "")
                    )
                except Exception:
                    error_message = response.text

                error = (
                    f"{model}: HTTP {response.status_code}: "
                    f"{error_message[:300]}"
                )
                errors.append(error)
                print(f"Gemini model failed: {error}")
                continue

            data = response.json()
            candidates = data.get("candidates", [])

            if not candidates:
                error = f"{model}: No response candidates returned."
                errors.append(error)
                print(error)
                continue

            candidate = candidates[0]

            # A candidate may be blocked or have no usable response.
            parts = candidate.get("content", {}).get("parts", [])
            text = "\n".join(
                part.get("text", "")
                for part in parts
                if part.get("text")
            )

            if not text.strip():
                error = (
                    f"{model}: Empty response. "
                    f"Finish reason: {candidate.get('finishReason', 'unknown')}"
                )
                errors.append(error)
                print(error)
                continue

            text = re.sub(r"^```(?:json)?\s*", "", text.strip())
            text = re.sub(r"\s*```$", "", text)

            try:
                result = json.loads(text)
            except json.JSONDecodeError as exc:
                error = f"{model}: Invalid JSON response: {exc}"
                errors.append(error)
                print(error)
                continue

            print(f"Gemini generation succeeded with model: {model}")
            return result

        except requests.exceptions.Timeout:
            error = f"{model}: Request timed out after {timeout} seconds."
            errors.append(error)
            print(error)
            continue

        except requests.exceptions.RequestException as exc:
            error = f"{model}: Network request failed: {exc}"
            errors.append(error)
            print(error)
            continue

        except Exception as exc:
            error = f"{model}: Unexpected error: {exc}"
            errors.append(error)
            print(error)
            continue

    # Every configured model failed.
    raise RuntimeError(
        "All Gemini models failed. Details: "
        + " | ".join(errors)
    )


GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

# Try the faster model first
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
).strip()

DEFAULT_FALLBACK_MODELS = [
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-3.6-flash",
    "gemini-3.8-flash",
]

_env_fallback_models = os.getenv(
    "GEMINI_FALLBACK_MODELS", ""
).strip()

if _env_fallback_models:
    DEFAULT_FALLBACK_MODELS = [
        model.strip()
        for model in _env_fallback_models.split(",")
        if model.strip()
    ]



def predict_justification_score_api(
    student_justification="",
    model_justification="",
    student_answer="",
    expected_answer="",
    question="",
    options="",
    **kwargs,
):
    """Return a score between 0 and 100, or None if Gemini fails."""
    student = (student_justification or student_answer or "").strip()
    expected = (model_justification or expected_answer or "").strip()

    if not student:
        return 0.0

    prompt = f"""
Evaluate the student's written reasoning for an academic assessment.

Return JSON only:
{{"score": 75, "feedback": "Specific feedback"}}

Give a score from 0 to 100 based on conceptual accuracy, relevance,
reasoning and completeness. Accept correct explanations in different words.
Do not judge solely by keyword overlap. Do not invent facts about the response.

Question: {question}
Options: {options}
Expected reasoning: {expected}
Student reasoning: {student}
"""
    try:
        result = _gemini(prompt)
        score = float(result["score"])
        return max(0.0, min(100.0, score))
    except Exception as exc:
        print("Gemini scoring failed:", str(exc))
        return None


def predict_justification_evaluation_api(
    student_justification="",
    model_justification="",
    student_answer="",
    expected_answer="",
    question="",
    options="",
    **kwargs,
):
    """Return score and feedback. Raise on API failure for app.py fallback."""
    student = (student_justification or student_answer or "").strip()
    expected = (model_justification or expected_answer or "").strip()

    if not student:
        return {
            "score": 0.0,
            "feedback": "No written justification was submitted.",
        }

    prompt = f"""
Evaluate this student's written reasoning fairly.

Return JSON only in this format:
{{"score": 75, "feedback": "Explain what is correct or missing."}}

Rules:
- Score from 0 to 100.
- Assess conceptual accuracy, relevance, reasoning and completeness.
- Accept valid alternative wording and explanations.
- Do not award a high score based only on matching keywords.
- Feedback must be brief, specific and supported by the student's response.

Question: {question}
Options: {options}
Expected reasoning: {expected}
Student reasoning: {student}
"""
    result = _gemini(prompt)
    score = max(0.0, min(100.0, float(result["score"])))
    feedback = str(result.get("feedback", "")).strip()

    if not feedback:
        feedback = "Reviewed for accuracy, relevance and completeness."

    return {"score": score, "feedback": feedback}


def generate_mcqs_from_notes_api(
    notes_text="",
    num_mcqs=3,
    topic_name="",
    target_topic="",
    generation_mode="pasted_notes",
    difficulty="Mixed",
    question_type="MCQ",
):
    """Generate MCQs directly using Gemini."""
    try:
        count = max(1, min(int(num_mcqs), 50))
        notes = (notes_text or "").strip()

        if not notes:
            raise ValueError("Please provide notes for question generation.")

        prompt = f"""
You are Quentora's educational question generator.

Generate {count} questions from the supplied notes.
Topic: {topic_name or "Use the notes"}
Target topic: {target_topic or "Main concepts"}
Generation mode: {generation_mode}
Difficulty: {difficulty}
Question type: {question_type}

Return JSON only, with this structure:
{{
  "mcqs": [
    {{
      "question": "Question text",
      "option_a": "First option",
      "option_b": "Second option",
      "option_c": "Third option",
      "option_d": "Fourth option",
      "correct_option": "A",
      "model_justification": "Explain why the answer is correct.",
      "difficulty": "Easy",
      "question_type": "MCQ"
    }}
  ]
}}

Requirements:
- Create up to {count} valid questions based on the notes.
- Each MCQ must have four distinct options and one correct answer.
- correct_option must be A, B, C or D.
- Include a useful model_justification for later student evaluation.
- Use the requested difficulty. If Mixed, vary difficulty.
- Avoid duplicate questions and ambiguous choices.
- Do not invent facts unsupported by the notes.
- For True/False questions, use option_a=True, option_b=False,
  option_c=Not applicable, option_d=Not applicable.
  Set correct_option to A for True or B for False.
- Do not include Markdown fences or text outside the JSON object.

NOTES:
{notes[:30000]}
"""
        result = _gemini(prompt, timeout=180)
        items = result.get("mcqs", [])
        mcqs = []

        for item in items:
            if not isinstance(item, dict):
                continue

            q = str(item.get("question", "")).strip()
            a = str(item.get("option_a", "")).strip()
            b = str(item.get("option_b", "")).strip()
            c = str(item.get("option_c", "")).strip()
            d = str(item.get("option_d", "")).strip()
            correct = str(item.get("correct_option", "")).strip().upper()

            if not (q and a and b and correct in {"A", "B"}):
                if not (q and a and b and c and d and correct in {"A", "B", "C", "D"}):
                    continue

            mcqs.append({
                "question": q,
                "option_a": a,
                "option_b": b,
                "option_c": c,
                "option_d": d,
                "correct_option": correct,
                "model_justification": str(
                    item.get("model_justification", "")
                ).strip(),
                "difficulty": str(item.get("difficulty") or difficulty),
                "question_type": str(item.get("question_type") or question_type),
            })

        mcqs = mcqs[:count]
        returned = len(mcqs)

        return {
            "success": returned > 0,
            "partial_success": 0 < returned < count,
            "exact_success": returned == count,
            "requested_count": count,
            "returned_count": returned,
            "mcqs": mcqs,
            "message": f"Generated {returned} of {count} questions.",
            "error": None if returned else "No valid questions were returned.",
            "raw_output": json.dumps(result, ensure_ascii=False),
        }

    except Exception as exc:
        print("Gemini MCQ generation failed:", str(exc))
        return {
            "success": False,
            "partial_success": False,
            "exact_success": False,
            "requested_count": num_mcqs,
            "returned_count": 0,
            "mcqs": [],
            "message": "",
            "error": str(exc),
            "raw_output": "",
        }
