"""
Main FastAPI Application Gateway.
Provides RESTful endpoints for health monitoring, candidate fitment evaluation, and deep resume audits.
Serves static frontend assets and handles cross-origin requests.
"""

import os
import io
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pypdf import PdfReader

from config import get_settings, Settings
from models import (
    FitmentRequest,
    FitmentResponse,
    AuditRequest,
    AuditResponse,
)
from services import DecisionService


@lru_cache
def get_decision_service() -> DecisionService:
    """
    Returns a cached singleton instance of DecisionService.
    Reuses the AI client across multiple API requests.
    """
    return DecisionService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Validates environment configurations on server startup and logs readiness.
    """
    app_settings = get_settings()
    app_settings.validate()
    print("FASTAPI SERVER INITIALIZED")
    print(f"Server listening on http://{app_settings.SERVER_HOST}:{app_settings.SERVER_PORT}")
    print(f"Decision Model: {app_settings.DECISION_MODEL}")
    print(f"Audit Model: {app_settings.AUDIT_MODEL}")
    yield
    print("FastAPI server shut down cleanly.")


# Initialize FastAPI application
app = FastAPI(
    title="AI Job Resume Fitment Matcher",
    description="High speed System-1 fitment decisions powered by Google Gemini Decision-1.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure Cross-Origin Resource Sharing (CORS) for external access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory if it exists
static_directory_path = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_directory_path):
    app.mount("/static", StaticFiles(directory=static_directory_path), name="static")


@app.get("/", tags=["Frontend"])
def serve_frontend_interface() -> FileResponse:
    """
    Serves the primary HTML frontend interface.
    """
    index_file_path = os.path.join(static_directory_path, "index.html")
    if os.path.exists(index_file_path):
        return FileResponse(index_file_path)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Frontend interface file index.html was not found."
    )


@app.get("/favicon.ico", include_in_schema=False)
def serve_favicon() -> FileResponse:
    """
    Serves application favicon icon file.
    """
    favicon_png_path = os.path.join(static_directory_path, "favicon.png")
    if os.path.exists(favicon_png_path):
        return FileResponse(favicon_png_path)
    return FileResponse(os.path.join(static_directory_path, "favicon.svg"))


@app.get("/health", tags=["System"])
def health_check(app_settings: Settings = Depends(get_settings)) -> Dict[str, Any]:
    """
    Health check endpoint returning system status and active model configurations.
    """
    return {
        "status": "healthy",
        "service": "job-fitment-matcher",
        "decision_model": app_settings.DECISION_MODEL,
        "audit_model": app_settings.AUDIT_MODEL,
        "server_port": app_settings.SERVER_PORT,
    }


@app.post("/api/evaluate-fitment", response_model=FitmentResponse, tags=["Evaluation"])
def evaluate_fitment(
    request: FitmentRequest,
    service: DecisionService = Depends(get_decision_service)
) -> FitmentResponse:
    """
    Receives Job Description and Candidate Resume, executes single-pass Gemini Decision,
    and returns calibrated eligibility, match tier, and rubric scores with zero output tokens.
    """
    try:
        return service.evaluate_fitment(request)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Candidate fitment evaluation failed: {str(error)}"
        )


@app.post("/api/deep-audit", response_model=AuditResponse, tags=["Audit"])
def generate_deep_audit(
    request: AuditRequest,
    service: DecisionService = Depends(get_decision_service)
) -> AuditResponse:
    """
    Executes an on-demand System-2 deep resume audit using gemini-3.5-flash-lite.
    Returns structured feedback on missing skills, resume red flags, and recommendations.
    """
    try:
        return service.generate_deep_audit(request)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Deep resume audit failed: {str(error)}"
        )


@app.post("/api/extract-pdf", tags=["Utility"])
async def extract_pdf_content(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extracts text content from an uploaded resume PDF file entirely in memory.
    Enforces a strict 5MB file size limit and valid PDF format.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files (.pdf) are supported."
        )

    content_bytes = await file.read()
    max_size_bytes = 5 * 1024 * 1024  # 5 Megabytes
    if len(content_bytes) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size exceeds the 5MB limit. Please upload a smaller PDF."
        )

    try:
        pdf_stream = io.BytesIO(content_bytes)
        reader = PdfReader(pdf_stream)
        extracted_text_pages = []

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                extracted_text_pages.append(page_text.strip())

        extracted_text = "\n\n".join(extracted_text_pages).strip()

        if not extracted_text or len(extracted_text) < 10:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Unable to extract text from this PDF. It may be an image scan or password-protected."
            )

        return {
            "text": extracted_text,
            "filename": file.filename,
            "pages": len(reader.pages),
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process PDF file: {str(exc)}"
        )


if __name__ == "__main__":
    import uvicorn
    server_settings = get_settings()
    uvicorn.run(
        "main:app",
        host=server_settings.SERVER_HOST,
        port=server_settings.SERVER_PORT,
        reload=True
    )
