# Use official Python image
FROM python:alpine

# Set the working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY src/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# Copy the FastAPI application code
COPY src/app/ /app/app/

# Expose the FastAPI application port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
