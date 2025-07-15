FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    curl \
    unzip \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install AutoSubSync specifically
RUN pip install --no-cache-dir autosubsync

# Copy the entire Bazarr codebase
COPY . .

# Create necessary directories
RUN mkdir -p /app/data/log \
    && mkdir -p /app/data/config \
    && mkdir -p /app/data/cache

# Set environment variables
ENV PYTHONPATH=/app
ENV BAZARR_CONFIG_DIR=/app/data/config
ENV BAZARR_LOG_DIR=/app/data/log

# Expose Bazarr port
EXPOSE 6767

# Create a startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting Bazarr with AutoSubSync integration..."\n\
echo "📋 Checking dependencies..."\n\
\n\
# Check AutoSubSync availability\n\
python3 -c "import autosubsync; print(f\"✅ AutoSubSync version: {getattr(autosubsync, \"__version__\", \"unknown\")}\")" || echo "❌ AutoSubSync not available"\n\
\n\
# Check FFmpeg\n\
ffmpeg -version > /dev/null 2>&1 && echo "✅ FFmpeg available" || echo "❌ FFmpeg not available"\n\
\n\
# Check if this is just a test run\n\
if [ "$1" = "test" ]; then\n\
    echo "🧪 Running integration test..."\n\
    python3 /app/test_autosubsync_integration.py\n\
    exit $?\n\
fi\n\
\n\
# Start Bazarr\n\
echo "🎬 Starting Bazarr on port 6767..."\n\
echo "🌐 Access at: http://localhost:6767"\n\
echo "⚙️  AutoSubSync will be available in Settings → Subtitles → Sync Method"\n\
cd /app && python3 bazarr.py --no-update --config /app/data/config\n\
' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:6767/api/system/status || exit 1

# Default command
CMD ["/app/start.sh"]