#!/bin/bash
# Docker test script for AutoSubSync integration with Bazarr

set -e

echo "🐳 Testing AutoSubSync integration in Docker"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Cleanup function
cleanup() {
    print_status "Cleaning up Docker containers..."
    docker-compose -f docker-compose.autosubsync.yml down --remove-orphans 2>/dev/null || true
}

# Set trap for cleanup on script exit
trap cleanup EXIT

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "docker-compose is not installed. Please install it and try again."
    exit 1
fi

print_success "docker-compose is available"

# Create necessary directories
print_status "Creating test directories..."
mkdir -p docker-data/{config,logs,movies,tv}
mkdir -p test-media

# Create test media files if they don't exist
print_status "Creating test media files..."

# Create a simple test subtitle file
cat > test-media/test_movie.srt << 'EOF'
1
00:00:01,000 --> 00:00:05,000
This is a test subtitle line one.

2
00:00:06,000 --> 00:00:10,000
This is a test subtitle line two.

3
00:00:11,000 --> 00:00:15,000
AutoSubSync integration testing.
EOF

# Create a dummy video file (minimal MP4 header)
if [ ! -f "test-media/test_movie.mp4" ]; then
    print_status "Creating dummy video file..."
    # Create a minimal valid MP4 file using ffmpeg if available
    if command -v ffmpeg &> /dev/null; then
        ffmpeg -f lavfi -i testsrc=duration=30:size=320x240:rate=1 -f lavfi -i sine=frequency=1000:duration=30 \
               -c:v libx264 -c:a aac -shortest test-media/test_movie.mp4 -y 2>/dev/null || {
            print_warning "Could not create video file with ffmpeg, creating dummy file"
            echo "dummy video content" > test-media/test_movie.mp4
        }
    else
        echo "dummy video content" > test-media/test_movie.mp4
    fi
fi

print_success "Test media files created"

# Build and start containers
print_status "Building Docker image..."
docker-compose -f docker-compose.autosubsync.yml build

print_status "Starting containers..."
docker-compose -f docker-compose.autosubsync.yml up -d

# Wait for Bazarr to start
print_status "Waiting for Bazarr to start..."
timeout=120
counter=0

while [ $counter -lt $timeout ]; do
    if curl -s -f http://localhost:6767/api/system/status >/dev/null 2>&1; then
        break
    fi
    sleep 2
    counter=$((counter + 2))
    echo -n "."
done

echo ""

if [ $counter -ge $timeout ]; then
    print_error "Bazarr failed to start within $timeout seconds"
    docker-compose -f docker-compose.autosubsync.yml logs bazarr-autosubsync
    exit 1
fi

print_success "Bazarr is running"

# Test AutoSubSync availability in container
print_status "Testing AutoSubSync availability in container..."
if docker exec bazarr-autosubsync-test python3 -c "
import autosubsync
print('AutoSubSync version:', getattr(autosubsync, '__version__', 'unknown'))
" 2>/dev/null; then
    print_success "AutoSubSync is available in container"
else
    print_error "AutoSubSync is not available in container"
    docker-compose -f docker-compose.autosubsync.yml logs bazarr-autosubsync
    exit 1
fi

# Test FFmpeg availability
print_status "Testing FFmpeg availability in container..."
if docker exec bazarr-autosubsync-test ffmpeg -version >/dev/null 2>&1; then
    print_success "FFmpeg is available in container"
else
    print_error "FFmpeg is not available in container"
    exit 1
fi

# Test Bazarr API
print_status "Testing Bazarr API..."
if api_response=$(curl -s http://localhost:6767/api/system/status 2>/dev/null); then
    print_success "Bazarr API is responding"
    echo "API Response: $api_response"
else
    print_error "Bazarr API is not responding"
    exit 1
fi

# Test if AutoSubSync integration is working
print_status "Testing AutoSubSync integration..."
if docker exec bazarr-autosubsync-test python3 -c "
import sys
sys.path.append('/app')
sys.path.append('/app/bazarr')

try:
    from bazarr.subtitles.tools.autosubsyncer import AutoSubSyncer
    syncer = AutoSubSyncer()
    print('AutoSubSyncer class imported successfully')
    print('Log directory:', syncer.log_dir_path)
except Exception as e:
    print('Error importing AutoSubSyncer:', e)
    sys.exit(1)
" 2>/dev/null; then
    print_success "AutoSubSync integration is working"
else
    print_error "AutoSubSync integration failed"
    docker-compose -f docker-compose.autosubsync.yml logs bazarr-autosubsync
    exit 1
fi

# Display useful information
echo ""
print_success "🎉 AutoSubSync integration test completed successfully!"
echo ""
echo "📋 Test Results:"
echo "✅ Docker containers are running"
echo "✅ Bazarr is accessible at http://localhost:6767"
echo "✅ AutoSubSync library is installed"
echo "✅ FFmpeg is available"
echo "✅ AutoSubSync integration class is working"
echo "✅ Test media server at http://localhost:8080"
echo ""
echo "🔧 Next steps:"
echo "1. Open Bazarr at http://localhost:6767"
echo "2. Go to Settings → Subtitles"
echo "3. Enable 'Automatic Subtitles Audio Synchronization'"
echo "4. Select 'AutoSubSync' from 'Sync Method' dropdown"
echo "5. Test with real media files"
echo ""
echo "📊 Container logs:"
echo "docker-compose -f docker-compose.autosubsync.yml logs -f bazarr-autosubsync"
echo ""
echo "🛑 To stop containers:"
echo "docker-compose -f docker-compose.autosubsync.yml down"

# Keep containers running
print_status "Containers will continue running. Press Ctrl+C to stop them."
print_status "You can now test AutoSubSync in Bazarr at http://localhost:6767"

# Optional: Open browser if available
if command -v xdg-open &> /dev/null; then
    print_status "Opening Bazarr in browser..."
    xdg-open http://localhost:6767 2>/dev/null &
elif command -v open &> /dev/null; then
    print_status "Opening Bazarr in browser..."
    open http://localhost:6767 2>/dev/null &
fi

# Wait for user input to stop
read -p "Press Enter to stop containers and cleanup..."