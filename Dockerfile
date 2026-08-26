# Start from an official Python base image
# "3.11-slim" = Python 3.11 on a minimal Debian base (smaller = faster pulls, less attack surface)
FROM python:3.11-slim

# Set the working directory inside the container
# All following commands run relative to /app, and the app lives here
WORKDIR /app

# Copy requirements FIRST, before the rest of the code
# This is a caching optimization: if requirements don't change,
# Docker reuses the cached dependency layer and skips reinstalling
COPY requirements.txt .

# Install the Python dependencies
# --no-cache-dir keeps the image smaller by not storing pip's download cache
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the rest of the application code
COPY app.py .

# Document which port the app listens on (informational)
EXPOSE 8080

# Create and switch to a non-root user for security
# (remember Phase 18 — running as non-root shrinks the blast radius if compromised)
RUN useradd -m appuser
USER appuser

# The command that runs when the container starts
CMD ["python", "app.py"]
