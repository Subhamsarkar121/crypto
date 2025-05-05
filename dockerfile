# Use official Python slim image
FROM python:3.9-slim

# Install curl (for healthcheck) as root
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and set environment
RUN useradd -m -u 1000 app
USER app

ENV HOME=/home/app \
    PATH=/home/app/.local/bin:$PATH

# Set working directory
WORKDIR /home/app

# Copy and install dependencies
COPY --chown=app:app requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY --chown=app:app . ./

# Expose Streamlit port
EXPOSE 7860

# Optional healthcheck (runs as app user)
HEALTHCHECK --interval=30s --timeout=5s \
  CMD curl --fail http://localhost:7860/_stcore/health || exit 1

# Launch the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=7860", "--server.address=0.0.0.0"]
