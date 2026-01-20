from datetime import datetime, timezone
import json
from typing import Any, Dict, Optional

import httpx
from app.config import get_settings
from app.helpers.years_helper import parse_years_to_float
from app.schemas.resume_schema import ExperienceSummary, ResumeSummary


class ResumeServiceError(Exception):
    """Raised when the resume service fails."""

class ResumeService:
    def __init__(self):
        self.settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
        }

    async def analyze_resume(self, resume_text: str, job_post: Optional[str]) -> ResumeSummary:
        """
        Main entry point to analyze resume resume_text using the LLM.
        """
        if not self.settings.openrouter_api_key:
            raise ResumeServiceError("OPENROUTER_API_KEY is not configured.")

        payload = self._build_payload(resume_text, job_post)

        async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
            try:
                response = await client.post(
                    f"{self.settings.openrouter_base_url}/chat/completions",
                    json=payload,
                    headers=self.headers,
                )
                response.raise_for_status()
            except Exception as exc:
                raise ResumeServiceError(f"OpenRouter request failed: {exc}") from exc

        return self._process_response(response.json())

    def _build_payload(self, resume_text: str, job_post: Optional[str]) -> Dict[str, Any]:
        """
        Building prompt payload for ATS AI checker
        """
        include_score = bool(job_post and job_post.strip())
        score_json = """
            "score": float (0.0 to 10.0),
        """
        now_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        """Constructs the LLM prompt and payload."""
        system_prompt = (
            "You are a concise resume ATS AI checker. Extract candidate details and assess relevancy. "
            "Return strict JSON with this format:"
            """
            {
                "name": "string",
                "location": "string",
                "work_experience": {
                    "role": "string",
                    "years": float,
                    "highlights": ["string"]
                },
                "skills": ["string"],
            """
                f"{score_json if include_score else ''}"
            """
                "feedbacks": ["string"],
            }
            """
            "'name','location', and 'work_experience' are based on the resume"
            "The 'role' must be only one specific"
            "The 'years' field must be a numeric float. Use null when unknown. Don't count irrelevant fieldwork experience with the current job position in the job post."
            f"{"The 'score' is a score for how relevant the resume is to the job post." if include_score else ''}"
            "The 'feedbacks' are feedbacks from you to improve the resume quality."
        )

        return {
            "model": self.settings.openrouter_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {   
                    "role": "user",
                    "content": f"""
                        RESUME:
                        {resume_text}

                        JOB POST:
                        {job_post}

                        NOW_DATE:{now_date}
                        """.strip()
                },
            ],
            "response_format": {"type": "json_object"},
        }

    def _process_response(self, resp_data: Dict[str, Any]) -> ResumeSummary:
        """Handles parsing, cleaning, and normalization of the LLM JSON."""
        try:
            content = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "")
            if not content:
                raise ValueError("LLM returned empty content.")

            # Robust JSON extraction
            content_str = content.strip()
            try:
                raw = json.loads(content_str)
            except json.JSONDecodeError:
                start, end = content_str.find("{"), content_str.rfind("}")
                if start == -1 or end == -1:
                    raise ValueError("No JSON object found in response.")
                raw = json.loads(content_str[start : end + 1])

            # Normalize Nested Data
            if "work_experience" in raw:
                raw["work_experience"] = self._normalize_work_experience(raw["work_experience"])

            return ResumeSummary.model_validate(raw)
        except Exception as exc:
            raise ResumeServiceError(f"Failed to parse LLM response: {exc}") from exc

    def _normalize_work_experience(self, value: Any) -> ExperienceSummary:
        """Converts various LLM outputs into a valid ExperienceSummary object."""
        if isinstance(value, dict):
            normalized_dict = value.copy()
            if "years" in normalized_dict:
                normalized_dict["years"] = parse_years_to_float(normalized_dict["years"])
            return ExperienceSummary.model_validate(normalized_dict)

        # Handle list-based responses from LLM
        highlights, role, years = [], None, None
        if isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    role = role or item.get("role") or item.get("title")
                    if years is None:
                        years = parse_years_to_float(item.get("years"))
                    
                    parts = [f"{k}: {v}" for k, v in item.items() 
                             if v and k not in {"role", "title", "position", "years"}]
                    if parts:
                        highlights.append("; ".join(parts))
                else:
                    highlights.append(str(item))

        return ExperienceSummary(role=role, years=years, highlights=highlights)