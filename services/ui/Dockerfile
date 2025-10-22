# Use the official Python image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /ui

# Copy the current directory contents (including requirements.txt)
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port
EXPOSE 8000

# Run the application (for your FastAPI service)
CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8000", "--server.address", "0.0.0.0", "--server.headless", "true"]
