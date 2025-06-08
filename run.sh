#!/bin/bash

echo "🚀 Starting Linguify Development Environment"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to check if port is in use
check_port() {
    local port=$1
    if netstat -an 2>/dev/null | grep ":$port " | grep -i listen >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start backend
start_backend() {
    log_info "Starting Django Backend..."
    cd backend
    
    # Check if Poetry is available
    if ! command -v poetry &> /dev/null; then
        log_info "Installing Poetry..."
        curl -sSL https://install.python-poetry.org | python3 -
        export PATH="$HOME/.local/bin:$PATH"
    fi
    
    # Install dependencies with Poetry
    log_info "Installing Python dependencies with Poetry..."
    poetry install
    
    # Run migrations
    log_info "Running database migrations..."
    poetry run python manage.py migrate
    
    # Start Django development server
    log_success "Starting Django server on http://localhost:8000"
    poetry run python manage.py runserver 0.0.0.0:8000 &
    DJANGO_PID=$!
    
    cd ..
}

# Function to start frontend
start_frontend() {
    log_info "Starting Next.js Frontend..."
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        npm install
    fi
    
    # Start Next.js development server
    log_success "Starting Next.js server on http://localhost:3000"
    npm run dev &
    NEXTJS_PID=$!
    
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo ""
    log_warning "Shutting down servers..."
    
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null || true
        log_info "Django server stopped"
    fi
    
    if [ ! -z "$NEXTJS_PID" ]; then
        kill $NEXTJS_PID 2>/dev/null || true
        log_info "Next.js server stopped"
    fi
    
    # Kill any remaining processes on ports 3000 and 8000
    pkill -f "manage.py runserver" 2>/dev/null || true
    pkill -f "next-server" 2>/dev/null || true
    
    log_success "Cleanup completed"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if ports are available (unless forced)
if [ "$1" != "--force" ]; then
    if check_port 8000; then
        log_error "Port 8000 is already in use."
        echo "Options:"
        echo "  1. Stop existing service: ./stop.sh"
        echo "  2. Force start anyway: ./run.sh --force"
        exit 1
    fi

    if check_port 3000; then
        log_error "Port 3000 is already in use."
        echo "Options:"
        echo "  1. Stop existing service: ./stop.sh"
        echo "  2. Force start anyway: ./run.sh --force"
        exit 1
    fi
else
    log_warning "Force mode: starting despite port conflicts"
fi

# Start services
start_backend
sleep 5  # Give Django more time to start

start_frontend
sleep 3  # Give Next.js time to start

echo ""
log_success "🎉 Linguify is now running!"
echo -e "${GREEN}================================${NC}"
echo -e "${BLUE}📖 Backend API:     ${NC}http://localhost:8000"
echo -e "${BLUE}⚛️  Frontend App:    ${NC}http://localhost:3000"
echo -e "${BLUE}🔧 Admin Panel:     ${NC}http://localhost:8000/admin"
echo -e "${BLUE}📚 API Docs:        ${NC}http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for processes to finish
wait $DJANGO_PID $NEXTJS_PID