# Use a base image with Python
FROM python:3.10-slim

# Set up the working directory
WORKDIR /app

# Copy your application files
COPY . /app

# Install any required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install cron
RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

# Create a cron file
RUN echo "0 2 * * 1 python3 /app/add_papers.py >> /var/log/cron.log 2>&1" > /etc/cron.d/add_papers_cron

# Give execution rights to the cron job
RUN chmod 0644 /etc/cron.d/add_papers_cron

# Apply the cron job
RUN crontab /etc/cron.d/add_papers_cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Start cron and the application
CMD cron && tail -f /var/log/cron.log
