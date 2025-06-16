#!/bin/bash

echo "🛑 Stopping Linguify Development Servers"
echo "========================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Kill Django processes
if pkill -f "manage.py runserver" 2>/dev/null; then
    log_success "Django server stopped"
else
    log_warning "No Django server found running"
fi

# Kill Next.js processes
if pkill -f "next-server\|npm run dev" 2>/dev/null; then
    log_success "Next.js server stopped"
else
    log_warning "No Next.js server found running"
fi

# Additional cleanup for Windows
if command -v taskkill >/dev/null 2>&1; then
    # Windows-specific cleanup
    for port in 8000 3000; do
        PID=$(netstat -ano 2>/dev/null | grep ":$port " | grep LISTENING | awk '{print $5}' | head -1)
        if [ ! -z "$PID" ]; then
            taskkill //PID $PID //F 2>/dev/null && log_success "Killed process on port $port"
        fi
    done
fi

echo ""
log_success "All servers stopped!"
echo "You can now start again with: ./run.sh"