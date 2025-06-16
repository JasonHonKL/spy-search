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
    && rm -rf /var/lib/apt/lists/*

# Copy all files first
COPY . .

# Convert line endings for shell scripts
RUN dos2unix installation.sh run.sh && \
    sed -i 's/\r$//' installation.sh && \
    sed -i 's/\r$//' run.sh && \
    chmod +x installation.sh run.sh

# Run installation.sh to install python packages, playwright, npm deps, etc.
RUN /bin/sh installation.sh

# Expose backend and frontend ports
EXPOSE 8000 8080

# Use run.sh as the container entrypoint
ENTRYPOINT ["/bin/sh", "run.sh"]