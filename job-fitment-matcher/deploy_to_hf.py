"""
Hugging Face Spaces Deployment Script.
Uploads job-fitment-matcher project files directly to the Space repository using HfApi.
"""

import os
import sys
from huggingface_hub import HfApi


def deploy(repo_id: str, token: str | None = None) -> None:
    """Deploy the current directory contents to Hugging Face Space."""
    hf_token = token or os.environ.get("HF_TOKEN")
    if not hf_token:
        print("Error: HF_TOKEN is required.")
        print("Pass it as an argument: python deploy_to_hf.py <USERNAME/SPACE_NAME> <HF_TOKEN>")
        print("Or set environment variable: export HF_TOKEN=hf_...")
        sys.exit(1)

    api = HfApi(token=hf_token)
    print(f"Connecting to Hugging Face Space: {repo_id}...")

    # Upload clean project directory excluding local environments and cache
    api.upload_folder(
        folder_path=".",
        repo_id=repo_id,
        repo_type="space",
        ignore_patterns=[
            ".env*",
            ".venv*",
            "__pycache__*",
            "*.pyc",
            "test_*",
            "deploy_to_hf.py",
        ],
    )

    print("Project files uploaded successfully!")
    print(f"Space URL: https://huggingface.co/spaces/{repo_id}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python deploy_to_hf.py <USERNAME/SPACE_NAME> [HF_TOKEN]")
        sys.exit(1)

    target_repo = sys.argv[1]
    auth_token = sys.argv[2] if len(sys.argv) > 2 else None
    deploy(target_repo, auth_token)
