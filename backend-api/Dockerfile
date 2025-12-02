# Dockerfile (Updated for Production)
FROM python:3.11-slim

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

EXPOSE 5000

# Use Gunicorn to run the app on port 5000
# The format is 'module_name:app_object' -> run:app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]