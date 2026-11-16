"""Schema-guided extraction: prompt with JSON schema -> validate with Pydantic
-> on failure retry once with the validation error fed back."""
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from google import genai
from google.genai import types

load_dotenv()

MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
_client = None


class ExtractionError(Exception):
    pass


def call_llm(system: str, prompt: str) -> str:
    """Only place that talks to an LLM provider. Swap this to change provider."""
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        _client = genai.Client(api_key=api_key) if api_key else genai.Client()
    response = _client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system,
        ),
    )
    return response.text or ""


def _strip_fences(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()


def extract_structured(text: str, model_cls: type[BaseModel], instructions: str) -> BaseModel:
    schema = json.dumps(model_cls.model_json_schema(), indent=2)
    system = (
        "You extract information into JSON. Output ONLY a JSON object that matches the "
        "schema. No prose, no markdown. Use only facts present in the input; never invent."
    )
    base_prompt = f"{instructions}\n\nJSON schema:\n{schema}\n\nInput:\n{text}"
    error = None
    for _attempt in range(2):
        prompt = base_prompt
        if error:
            prompt += f"\n\nYour previous output failed validation:\n{error}\nReturn corrected JSON only."
        raw = call_llm(system, prompt)
        try:
            return model_cls.model_validate_json(_strip_fences(raw))
        except ValidationError as e:
            error = str(e)
    raise ExtractionError(f"AI output failed validation after retry: {error}")


PROFILE_INSTRUCTIONS = (
    "Extract a candidate profile from this resume. For every skill, set level from the "
    "evidence and put a short supporting phrase from the resume in 'evidence'."
)
JD_INSTRUCTIONS = (
    "Extract role requirements from this job description. Rate each skill's importance "
    "1-5 based on how prominently the JD stresses it."
)
