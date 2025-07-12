# Build stage
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and setup files
COPY requirements.txt setup.py ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --user --no-cache-dir -r requirements.txt
RUN pip install --user --no-cache-dir .

# Runtime stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/home/seneca/.local/bin:$PATH

# Create non-root user
RUN useradd -m -u 1000 seneca

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/seneca/.local

# Copy application files
COPY --chown=seneca:seneca src/ ./src/
COPY --chown=seneca:seneca templates/ ./templates/
COPY --chown=seneca:seneca static/ ./static/
COPY --chown=seneca:seneca start_seneca.py ./
COPY --chown=seneca:seneca seneca_cli.py ./

# Create directories for logs (will be mounted as volumes)
RUN mkdir -p /logs && chown seneca:seneca /logs

# Switch to non-root user
USER seneca

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/health')"

# Default environment variables
ENV MARCUS_LOG_DIR=/logs \
    SENECA_HOST=0.0.0.0 \
    SENECA_PORT=8000

# Run the application
CMD ["python", "start_seneca.py"]