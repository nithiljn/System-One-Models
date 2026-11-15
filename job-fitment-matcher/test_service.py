"""
Automated Verification Test for DecisionService.
Tests both System-1 fast decisions and System-2 deep audit with live sample data.
"""

from services import DecisionService
from models import FitmentRequest, AuditRequest


def run_verification_tests() -> None:
    """Runs end-to-end tests against DecisionService and prints detailed results."""
    print("STARTING DECISION SERVICE VERIFICATION TESTS")

    service = DecisionService()

    sample_job = (
        "Senior Python Engineer. Requirements: 5+ years building backend APIs with FastAPI, "
        "production Docker deployments, Kubernetes orchestration, and PostgreSQL database optimization."
    )

    sample_matching_resume = (
        "Staff Software Engineer with 7 years of backend engineering experience. "
        "Built and maintained high-throughput microservices using Python and FastAPI. "
        "Managed multi-region Kubernetes clusters with Docker containers. "
        "Expert in PostgreSQL schema indexing and query optimization."
    )

    sample_mismatched_resume = (
        "Junior Graphic Designer with 1 year experience creating marketing posters, "
        "Figma wireframes, and Adobe Photoshop designs. Learning HTML and CSS basics."
    )

    # TEST 1: Matching Candidate Fitment
    print("\n--- TEST 1: Matching Candidate (Expected Strong Fit) ---")
    req_match = FitmentRequest(
        job_description=sample_job,
        resume_content=sample_matching_resume
    )
    res_match = service.evaluate_fitment(req_match)
    print(f"Eligible: {res_match.is_eligible} (Confidence: {res_match.eligibility_confidence * 100:.1f}%)")
    print(f"Fit Tier: {res_match.fit_tier} (Confidence: {res_match.tier_confidence * 100:.1f}%)")
    print(f"Match Score: {res_match.match_score} / 10.0")
    print(f"Has Dealbreakers: {res_match.has_dealbreakers}")
    print(f"Latency: {res_match.latency_ms} ms")
    print(f"Output Tokens Billed: {res_match.output_tokens_billed}")

    assert res_match.is_eligible is True, "Matching candidate should be eligible."
    assert res_match.match_score >= 6.0, "Matching candidate score should be >= 6.0."
    print("TEST 1 PASSED!")

    # TEST 2: Mismatched Candidate Fitment
    print("\n--- TEST 2: Mismatched Candidate (Expected Skill Gap) ---")
    req_mismatch = FitmentRequest(
        job_description=sample_job,
        resume_content=sample_mismatched_resume
    )
    res_mismatch = service.evaluate_fitment(req_mismatch)
    print(f"Eligible: {res_mismatch.is_eligible} (Confidence: {res_mismatch.eligibility_confidence * 100:.1f}%)")
    print(f"Fit Tier: {res_mismatch.fit_tier}")
    print(f"Match Score: {res_mismatch.match_score} / 10.0")
    print(f"Has Dealbreakers: {res_mismatch.has_dealbreakers}")
    print(f"Latency: {res_mismatch.latency_ms} ms")

    assert res_mismatch.is_eligible is False, "Mismatched candidate should not be eligible."
    assert res_mismatch.match_score < 5.0, "Mismatched candidate score should be < 5.0."
    print(" TEST 2 PASSED!")

    # TEST 3: System-2 Deep Audit Generation
    print("\n--- TEST 3: System-2 Deep Audit Generation ---")
    audit_req = AuditRequest(
        job_description=sample_job,
        resume_content=sample_mismatched_resume
    )
    audit_res = service.generate_deep_audit(audit_req)
    print(f"Missing Skills Identified: {len(audit_res.missing_skills)}")
    for skill in audit_res.missing_skills[:3]:
        print(f"  * {skill}")
    print(f"Red Flags Identified: {len(audit_res.resume_red_flags)}")
    for flag in audit_res.resume_red_flags[:2]:
        print(f"  * {flag}")
    print(f"Audit Latency: {audit_res.latency_ms} ms")

    assert len(audit_res.missing_skills) > 0, "Audit should identify missing skills."
    print("TEST 3 PASSED!")

    print("ALL 3 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    


if __name__ == "__main__":
    run_verification_tests()
