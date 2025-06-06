#!/bin/bash

# Linguify Development Server Launcher
# This script starts both the Django backend and Next.js frontend

set -e

echo "🚀 Starting Linguify Development Environment"
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to start backend
start_backend() {
    echo -e "${BLUE}📖 Starting Django Backend (Port 8000)...${NC}"
    cd backend
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || {
        echo -e "${RED}❌ Failed to activate virtual environment${NC}"
        exit 1
    }
    
    # Install dependencies if needed
    if [ ! -f ".deps_installed" ]; then
        echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
        pip install -r requirements.txt
        touch .deps_installed
    fi
    
    # Run migrations
    echo -e "${BLUE}🔧 Running database migrations...${NC}"
    python manage.py migrate
    
    # Start Django development server
    echo -e "${GREEN}✅ Starting Django server on http://localhost:8000${NC}"
    python manage.py runserver 0.0.0.0:8000 &
    DJANGO_PID=$!
    
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${BLUE}⚛️  Starting Next.js Frontend (Port 3000)...${NC}"
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
        npm install
    fi
    
    # Start Next.js development server
    echo -e "${GREEN}✅ Starting Next.js server on http://localhost:3000${NC}"
    npm run dev &
    NEXTJS_PID=$!
    
    cd ..
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    
    if [ ! -z "$DJANGO_PID" ]; then
        kill $DJANGO_PID 2>/dev/null
        echo -e "${BLUE}📖 Django server stopped${NC}"
    fi
    
    if [ ! -z "$NEXTJS_PID" ]; then
        kill $NEXTJS_PID 2>/dev/null
        echo -e "${BLUE}⚛️  Next.js server stopped${NC}"
    fi
    
    # Kill any remaining processes on ports 3000 and 8000
    pkill -f "manage.py runserver" 2>/dev/null || true
    pkill -f "next-server" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if ports are available
if check_port 8000; then
    echo -e "${RED}❌ Port 8000 is already in use. Please stop the existing service.${NC}"
    exit 1
fi

if check_port 3000; then
    echo -e "${RED}❌ Port 3000 is already in use. Please stop the existing service.${NC}"
    exit 1
fi

# Start services
start_backend
sleep 3  # Give Django time to start

start_frontend
sleep 3  # Give Next.js time to start

echo ""
echo -e "${GREEN}🎉 Linguify is now running!${NC}"
echo -e "${GREEN}================================${NC}"
echo -e "${BLUE}📖 Backend API:     ${NC}http://localhost:8000"
echo -e "${BLUE}⚛️  Frontend App:    ${NC}http://localhost:3000"
echo -e "${BLUE}🔧 Admin Panel:     ${NC}http://localhost:8000/admin"
echo -e "${BLUE}📚 API Docs:        ${NC}http://localhost:8000/api/docs"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for processes to finish
wait $DJANGO_PID $NEXTJS_PID