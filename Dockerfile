FROM python:3.11-slim

WORKDIR /app

# Install the PostgreSQL client library that psycopg2 needs at runtime
# apt-get update refreshes the package list, then we install libpq5
# We clean up apt cache afterward to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

RUN useradd -m appuser
USER appuser

CMD ["python", "app.py"]
