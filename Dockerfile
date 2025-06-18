# Use python 3.13 slim as base image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies for npm, playwright, and building packages
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    ca-certificates \
    build-essential \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm-dev \
    libasound2 \
    libpangocairo-1.0-0 \
    libgtk-3-0 \
    libxshmfence1 \
    libglib2.0-0 \
    npm \
    dos2unix \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv globally
RUN pip install --no-cache-dir uv

# Copy requirements first for better caching
COPY requirements.txt ./
COPY frontend/package*.json ./frontend/

# Copy the rest of the application
COPY . .

# Convert line endings for shell scripts and make executable
RUN dos2unix installation.sh run.sh && \
    sed -i 's/\r$//' installation.sh && \
    sed -i 's/\r$//' run.sh && \
    chmod +x installation.sh run.sh

# Run installation.sh to install python packages, playwright, npm deps, etc.
RUN bash installation.sh

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080 || exit 1

# Expose both ports for local testing
EXPOSE 8080
EXPOSE 8000

# Use run.sh as the container entrypoint
ENTRYPOINT ["bash", "run.sh"]