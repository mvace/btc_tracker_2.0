# Use the official Python image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /portfolio_service

# Copy the current directory contents (including requirements.txt)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# Expose the port
EXPOSE 8000

# Run the application (for your FastAPI service)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
