"""
Automated Verification Tests for FastAPI Endpoints.
Uses Starlette TestClient to test health, evaluation, and validation error handling.
"""

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_suite() -> None:
    """Executes end-to-end integration tests for all exposed API endpoints."""
    print("==================================================")
    print("🧪 RUNNING FASTAPI ENDPOINT AUTOMATED TESTS")
    print("==================================================")

    # 1. TEST HEALTH ENDPOINT
    print("\n--- TEST 1: Health Check Endpoint (GET /health) ---")
    response = client.get("/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.json()}")
    assert response.status_code == 200, "Health check should return HTTP 200."
    assert response.json()["status"] == "healthy", "Service status must be healthy."
    print("✅ TEST 1 PASSED!")

    # 2. TEST FRONTEND ROUTE
    print("\n--- TEST 2: Frontend Route (GET /) ---")
    frontend_response = client.get("/")
    print(f"Status Code: {frontend_response.status_code}")
    assert frontend_response.status_code == 200, "Root route should return HTTP 200."
    print("✅ TEST 2 PASSED!")

    # 3. TEST VALIDATION REJECTION ON EMPTY INPUT
    print("\n--- TEST 3: Validation Error Handling (POST /api/evaluate-fitment with empty payload) ---")
    invalid_payload = {
        "job_description": "   ",
        "resume_content": "short"
    }
    invalid_response = client.post("/api/evaluate-fitment", json=invalid_payload)
    print(f"Status Code: {invalid_response.status_code} (Expected 422 Unprocessable Entity)")
    assert invalid_response.status_code == 422, "Invalid input must be rejected with HTTP 422."
    print("✅ TEST 3 PASSED!")

    # 4. TEST LIVE FITMENT EVALUATION
    print("\n--- TEST 4: Live Fitment Evaluation (POST /api/evaluate-fitment) ---")
    valid_payload = {
        "job_description": (
            "Senior Backend Engineer. Must have 5+ years building distributed APIs in Python, "
            "production experience with FastAPI and PostgreSQL, and container orchestration with Docker."
        ),
        "resume_content": (
            "Lead Software Engineer with 6 years experience in Python and FastAPI. "
            "Designed high-concurrency microservices deployed in Docker containers on AWS. "
            "Deep experience with PostgreSQL query tuning and database migrations."
        )
    }
    eval_response = client.post("/api/evaluate-fitment", json=valid_payload)
    print(f"Status Code: {eval_response.status_code}")
    eval_data = eval_response.json()
    print(f"Eligible: {eval_data['is_eligible']} (Confidence: {eval_data['eligibility_confidence'] * 100:.1f}%)")
    print(f"Fit Tier: {eval_data['fit_tier']} (Confidence: {eval_data['tier_confidence'] * 100:.1f}%)")
    print(f"Match Score: {eval_data['match_score']} / 10.0")
    print(f"Latency: {eval_data['latency_ms']} ms")
    print(f"Tokens Billed: {eval_data['output_tokens_billed']}")

    assert eval_response.status_code == 200, "Valid evaluation must return HTTP 200."
    assert eval_data["is_eligible"] is True, "Matching candidate should be eligible."
    assert eval_data["output_tokens_billed"] == 0, "Output tokens billed must be 0."
    print("✅ TEST 4 PASSED!")

    # 5. TEST PDF TEXT EXTRACTION ENDPOINT
    print("\n--- TEST 5: PDF Text Extraction (POST /api/extract-pdf) ---")
    sample_pdf_bytes = b"""%PDF-1.4
1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj
2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj
3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj
4 0 obj << /Length 55 >> stream
BT
/F1 12 Tf
72 712 Td
(Software Engineer with Python skills) Tj
ET
endstream endobj
5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj
xref
0 6
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000244 00000 n 
0000000350 00000 n 
trailer << /Size 6 /Root 1 0 R >>
startxref
426
%%EOF"""
    files = {"file": ("my_resume.pdf", sample_pdf_bytes, "application/pdf")}
    pdf_response = client.post("/api/extract-pdf", files=files)
    print(f"Status Code: {pdf_response.status_code}")
    pdf_data = pdf_response.json()
    print(f"Extracted: {pdf_data.get('text')}")
    print(f"Filename: {pdf_data.get('filename')}")
    print(f"Pages: {pdf_data.get('pages')}")

    assert pdf_response.status_code == 200, "PDF extraction must return HTTP 200."
    assert "Software Engineer with Python skills" in pdf_data["text"]
    assert pdf_data["pages"] == 1
    print("✅ TEST 5 PASSED!")

    print("\n==================================================")
    print("🎉 ALL 5 FASTAPI AUTOMATED TESTS PASSED!")
    print("==================================================")


if __name__ == "__main__":
    test_api_suite()
