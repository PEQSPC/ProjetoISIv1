# Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Copy requirements first to leverage Docker cache
COPY ./src/requirements.txt /code/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy source code
COPY ./src /code

# Expose port 8000
EXPOSE 8000

# Run with standard FastAPI command (Production mode)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]