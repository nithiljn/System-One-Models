# Production Dockerfile for AI Job-Resume Fitment Matcher
# Built for Hugging Face Spaces (UID 1000 non-root user, port 7860)

FROM python:3.12-slim

# Create a non-root user with UID 1000 (Required by Hugging Face Spaces Docker SDK)
RUN useradd -m -u 1000 user

# Switch to non-root user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set application working directory inside container
WORKDIR $HOME/app

# Copy dependency specifications first to leverage Docker layer caching
COPY --chown=user:user requirements.txt .

# Install dependencies without root privileges and clean build cache
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code into container
COPY --chown=user:user . .

# Expose Hugging Face Spaces default port
EXPOSE 7860

# Launch FastAPI ASGI server via Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
