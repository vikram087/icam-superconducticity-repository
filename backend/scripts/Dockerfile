# Use Python slim image for a smaller, faster base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy only requirements first to cache pip installs
COPY requirements.txt /app/

# Install Python dependencies
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip install -r /app/requirements.txt

# Copy the rest of the application files
COPY . /app/

# Set entrypoint to use virtualenv and run the script
# CMD ["/app/venv/bin/python", "add_papers.py"]
