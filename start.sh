#!/bin/bash

# TeleCommand Pro Launcher
# Starts both the bot and web portal

echo "======================================"
echo "  TeleCommand Pro - Starting Services "
echo "====================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run ./setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if config.json exists
if [ ! -f "config.json" ]; then
    echo "❌ config.json not found!"
    echo "Please create config.json from config.example.json"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $BOT_PID $PORTAL_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Web Portal
echo "🌐 Starting Web Portal..."
python3 web_portal.py &
PORTAL_PID=$!
sleep 2

# Check if portal started
if ! ps -p $PORTAL_PID > /dev/null; then
    echo "❌ Failed to start web portal"
    exit 1
fi

echo "✅ Web Portal running (PID: $PORTAL_PID)"
echo "   Access at: http://localhost:5000"
echo ""

# Start Bot
echo "🤖 Starting TeleCommand Pro Bot..."
python3 bot.py &
BOT_PID=$!
sleep 2

# Check if bot started
if ! ps -p $BOT_PID > /dev/null; then
    echo "❌ Failed to start bot"
    kill $PORTAL_PID 2>/dev/null
    exit 1
fi

echo "✅ Bot running (PID: $BOT_PID)"
echo ""

echo "======================================"
echo "   All Services Running!              "
echo "======================================"
echo ""
echo "🌐 Web Portal: http://localhost:5000"
echo ""
echo "🤖 Bot: Running and waiting for commands"
echo ""
echo "ℹ️  Contact administrator for login credentials"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
wait
