# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Default interval (600 seconds)
ENV RUN_INTERVAL=600

# Ensure config folder exists (in case user forgets to mount one)
RUN mkdir -p /app/config

# Use start.sh as the container entrypoint
ENTRYPOINT ["/bin/sh", "/app/start.sh"]
