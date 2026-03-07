#!/bin/bash
set -e

echo ""
echo "  ╔══════════════════════════════════════════╗"
echo "  ║   🖥️  Building VPS Base Docker Image     ║"
echo "  ╚══════════════════════════════════════════╝"
echo ""

docker build \
    -f Dockerfile.vps \
    -t telegram-bot-vps-base \
    .

echo ""
echo "✅ Base image built successfully: telegram-bot-vps-base"
echo ""
echo "─────────────────────────────────────────────"
echo "⚠️  IMPORTANT: .env file mein VPS_HOST_IP set karo!"
echo "   Example: VPS_HOST_IP=123.45.67.89"
echo ""
echo "🔌 Port range used: 32000–33000"
echo "   Ensure these ports are open in your firewall:"
echo "  sudo ufw allow 32000:33000/tcp"
echo "─────────────────────────────────────────────"
echo ""
echo "🚀 Bot start karne ke liye:"
echo "   python3 bot.py"
echo ""
