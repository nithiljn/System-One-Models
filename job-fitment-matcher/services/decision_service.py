"""
Core AI Decision Service.
Orchestrates fast System-1 decisions via gemini-decision-1 and on-demand System-2 deep audits via gemini-3.8-flash.
"""

import json
import time
from typing import Dict, Any, List
from google import genai
from config import get_settings
from models import (
    FitmentRequest,
    FitmentResponse,
    AuditRequest,
    AuditResponse,
)


class DecisionService:
    """
    AI Service encapsulating all interactions with Google AI Studio.
    Handles decision evaluation, rubric scoring, confidence mapping, and resume auditing.
    """

    def __init__(self) -> None:
        """
        Initializes Google GenAI client with cached application settings.
        Targets the v1beta endpoint required by the Decisions API.
        """
        self.settings = get_settings()
        self.client = genai.Client(
            api_key=self.settings.GEMINI_API_KEY,
            http_options={"api_version": "v1beta"}
        )

    def evaluate_fitment(self, request: FitmentRequest) -> FitmentResponse:
        """
        Executes a single pass multimodal decision on the candidate resume against the job description.
        Evaluates eligibility, fitment category, rubric score, and dealbreakers in one pass with zero output tokens.
        """
        # Format the combined context for the model
        combined_context = (
            f"[TARGET JOB DESCRIPTION]\n"
            f"{request.job_description}\n\n"
            f"[CANDIDATE RESUME]\n"
            f"{request.resume_content}"
        )

        # Define the 4 structured questions
        decision_questions: Dict[str, Any] = {
            "is_eligible": {
                "type": "noul",
                "instructions": (
                    "Does this candidate satisfy the fundamental qualifications, skills, "
                    "and core experience required by the job description?"
                ),
            },
            "fit_tier": {
                "type": "choice",
                "instructions": "What is the overall fitment level of the candidate for this role?",
                "criteria": {
                    "Strong Match": "Candidate meets or exceeds all core technical skills and experience levels.",
                    "Moderate Match": "Candidate meets most skills but has slight experience gaps or minor missing tools.",
                    "Skill Gap": "Candidate lacks several essential technologies or has insufficient relevant experience.",
                },
            },
            "match_score": {
                "type": "score",
                "instructions": "Rate the candidate's alignment with the job description on a 0 to 10 scale.",
                "criteria": [
                    "Level 0: No match or completely irrelevant profile.",
                    "Level 1: Minimal match with only elementary basic awareness.",
                    "Level 2: Weak match lacking almost all required production skills.",
                    "Level 3: Below average match with substantial technical gaps.",
                    "Level 4: Marginal match satisfying only superficial requirements.",
                    "Level 5: Moderate average fit meeting standard basic prerequisites.",
                    "Level 6: Fair match with competence in key common tools.",
                    "Level 7: Good match with dependable hands-on domain skills.",
                    "Level 8: Very strong candidate matching all primary competencies.",
                    "Level 9: Excellent match with deep production expertise.",
                    "Level 10: Perfect fit exceeding requirements with outstanding alignment."
                ],
            },
            "has_dealbreakers": {
                "type": "noul",
                "instructions": (
                    "Are there strict, non-negotiable requirements explicitly stated in the job description "
                    "that are completely absent, unfulfilled, or violated by the candidate's profile?"
                ),
            },
        }

        # Start high-resolution timer to measure latency
        start_time = time.perf_counter()

        # Call Gemini Decisions API
        result = self.client.decisions.create(
            model=self.settings.DECISION_MODEL,
            input=combined_context,
            questions=decision_questions,
        )

        # Stop timer and calculate latency in milliseconds
        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Extract question answers
        eligible_answer = result.answers["is_eligible"]
        tier_answer = result.answers["fit_tier"]
        score_answer = result.answers["match_score"]
        dealbreaker_answer = result.answers["has_dealbreakers"]

        # Parse boolean values and confidence thresholds
        is_eligible_bool = eligible_answer.noul >= 0.5
        eligibility_conf = round(float(eligible_answer.confidence), 4)

        fit_tier_str = tier_answer.choice
        tier_conf = round(float(tier_answer.confidence), 4)

        calculated_score = round(float(score_answer.score), 1)

        has_dealbreakers_bool = dealbreaker_answer.noul >= 0.5
        dealbreaker_conf = round(float(dealbreaker_answer.confidence), 4)

        return FitmentResponse(
            is_eligible=is_eligible_bool,
            eligibility_confidence=eligibility_conf,
            fit_tier=fit_tier_str,
            tier_confidence=tier_conf,
            match_score=calculated_score,
            has_dealbreakers=has_dealbreakers_bool,
            dealbreaker_confidence=dealbreaker_conf,
            latency_ms=latency_ms,
            output_tokens_billed=0,
        )

    def generate_deep_audit(self, request: AuditRequest) -> AuditResponse:
        """
        Executes an on-demand System-2 deep audit using gemini-3.8-flash.
        Identifies missing skills, red flags, and concrete recommendations in structured JSON.
        """
        audit_prompt = (
            "You are an expert technical recruiter and resume auditor. "
            "Compare the candidate resume against the job description below. "
            "Provide an objective, constructive critique formatted strictly as valid JSON.\n\n"
            "Return JSON matching exactly this schema:\n"
            "{\n"
            '  "missing_skills": ["skill 1", "skill 2"],\n'
            '  "resume_red_flags": ["issue 1", "issue 2"],\n'
            '  "actionable_recommendations": ["step 1", "step 2"]\n'
            "}\n\n"
            f"[TARGET JOB DESCRIPTION]\n{request.job_description}\n\n"
            f"[CANDIDATE RESUME]\n{request.resume_content}\n"
        )

        start_time = time.perf_counter()

        # Call generative model with strict JSON response MIME type
        response = self.client.models.generate_content(
            model=self.settings.AUDIT_MODEL,
            contents=audit_prompt,
            config={"response_mime_type": "application/json"}
        )

        latency_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Parse returned JSON structure safely
        try:
            parsed_data = json.loads(response.text)
        except (json.JSONDecodeError, TypeError):
            parsed_data = {
                "missing_skills": ["Unable to parse skills output."],
                "resume_red_flags": ["Model returned unstructured output."],
                "actionable_recommendations": ["Please review profile manually."]
            }

        return AuditResponse(
            missing_skills=parsed_data.get("missing_skills", []),
            resume_red_flags=parsed_data.get("resume_red_flags", []),
            actionable_recommendations=parsed_data.get("actionable_recommendations", []),
            latency_ms=latency_ms,
        )
