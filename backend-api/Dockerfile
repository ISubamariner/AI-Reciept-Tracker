# Dockerfile (Updated with uv for faster installation)
FROM python:3.11-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /usr/src/app

# Copy dependency files
COPY requirements.txt ./

# Install dependencies using uv (much faster than pip)
RUN uv pip install --system --no-cache -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 5000

# Use Gunicorn to run the app on port 5000
# The format is 'module_name:app_object' -> run:app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]