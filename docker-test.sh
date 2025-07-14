#!/bin/bash

# Docker testing script for Bazarr AutoSubSync integration
set -e

echo "🐳 Bazarr AutoSubSync Docker Test Script"
echo "========================================"

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

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    print_error "Docker is not running! Please start Docker first."
    exit 1
fi

print_success "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    print_warning "docker-compose not found, trying docker compose..."
    COMPOSE_CMD="docker compose"
else
    COMPOSE_CMD="docker-compose"
fi

# Create test media directory
mkdir -p test_media
print_status "Created test_media directory"

# Function to run integration test
test_integration() {
    print_status "Running AutoSubSync integration test..."
    
    if $COMPOSE_CMD --profile test run --rm bazarr-test; then
        print_success "Integration test passed!"
        return 0
    else
        print_error "Integration test failed!"
        return 1
    fi
}

# Function to build and start Bazarr
start_bazarr() {
    print_status "Building Bazarr with AutoSubSync..."
    
    if $COMPOSE_CMD build bazarr-autosubsync; then
        print_success "Build completed successfully"
    else
        print_error "Build failed!"
        exit 1
    fi
    
    print_status "Starting Bazarr container..."
    $COMPOSE_CMD up -d bazarr-autosubsync
    
    print_status "Waiting for Bazarr to start..."
    sleep 10
    
    # Check if container is running
    if docker ps | grep -q bazarr-autosubsync-test; then
        print_success "Bazarr is running!"
        print_status "🌐 Access Bazarr at: http://localhost:6767"
        print_status "⚙️  Go to Settings → Subtitles to configure AutoSubSync"
        
        # Show logs
        echo ""
        print_status "Container logs:"
        $COMPOSE_CMD logs --tail=20 bazarr-autosubsync
    else
        print_error "Failed to start Bazarr container"
        $COMPOSE_CMD logs bazarr-autosubsync
        exit 1
    fi
}

# Function to stop containers
stop_containers() {
    print_status "Stopping containers..."
    $COMPOSE_CMD down
    print_success "Containers stopped"
}

# Function to show logs
show_logs() {
    print_status "Showing Bazarr logs..."
    $COMPOSE_CMD logs -f bazarr-autosubsync
}

# Function to show help
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  test     - Run integration test only"
    echo "  start    - Build and start Bazarr with AutoSubSync"
    echo "  stop     - Stop all containers"
    echo "  logs     - Show container logs"
    echo "  restart  - Restart containers"
    echo "  clean    - Stop containers and remove volumes"
    echo "  help     - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 test          # Run integration test"
    echo "  $0 start         # Start Bazarr"
    echo "  $0 logs          # Watch logs"
    echo "  $0 stop          # Stop everything"
}

# Main script logic
case "${1:-start}" in
    "test")
        print_status "Running integration test..."
        if $COMPOSE_CMD build bazarr-test; then
            test_integration
        else
            print_error "Failed to build test container"
            exit 1
        fi
        ;;
    "start")
        start_bazarr
        ;;
    "stop")
        stop_containers
        ;;
    "logs")
        show_logs
        ;;
    "restart")
        stop_containers
        sleep 2
        start_bazarr
        ;;
    "clean")
        print_status "Cleaning up containers and volumes..."
        $COMPOSE_CMD down -v
        docker system prune -f
        print_success "Cleanup completed"
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac