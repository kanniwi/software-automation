FROM python:3.14.0-slim-trixie

WORKDIR /app

# Install build/runtime deps and project requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . /app

# Use a Python entrypoint module (no shell scripts). The module will
# wait for Postgres, run migrations, then exec gunicorn.
CMD ["python", "-m", "app.entrypoint"]
