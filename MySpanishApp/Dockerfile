# Multi-stage Dockerfile for SpanishMaster PyQt6 Application
# Stage 1: Build environment
FROM python:3.11-slim as builder

# Install system dependencies for Qt6 and build tools
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libegl1-mesa \
    libxcb-cursor0 \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Qt
ENV QT_QPA_PLATFORM=xcb
ENV DISPLAY=:0

# Create app directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt pyproject.toml poetry.lock* ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --only=main --no-dev

# Stage 2: Production image
FROM python:3.11-slim as production

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libfontconfig1 \
    libx11-xcb1 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xfixes0 \
    libxcb-xinerama0 \
    libxkbcommon-x11-0 \
    libxkbcommon0 \
    libegl1-mesa \
    libxcb-cursor0 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN groupadd -r spanishmaster && useradd -r -g spanishmaster -s /bin/bash spanishmaster

# Set environment variables
ENV QT_QPA_PLATFORM=xcb
ENV DISPLAY=:0
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create app directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages/ /usr/local/lib/python3.11/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy application code
COPY --chown=spanishmaster:spanishmaster . .

# Create necessary directories
RUN mkdir -p logs data backups \
    && chown -R spanishmaster:spanishmaster /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)" || exit 1

# Switch to non-root user
USER spanishmaster

# Expose port for potential web interface
EXPOSE 8080

# Add labels for metadata
LABEL maintainer="brandon.lambert87@gmail.com" \
      version="0.1.0" \
      description="SpanishMaster - Advanced Spanish Learning Application" \
      org.opencontainers.image.source="https://github.com/bjpl/SpanishMaster"

# Default command
CMD ["python", "main.py"]