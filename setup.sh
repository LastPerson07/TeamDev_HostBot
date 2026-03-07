#!/bin/bash

#                      [TeamDev](https://team_x_og)
#          
#          Project Id -> 28.
#          Project Name -> Script Host.
#          Project Age -> 4Month+ (Updated On 07/03/2026)
#          Project Idea By -> @MR_ARMAN_08
#          Project Dev -> @MR_ARMAN_08
#          Powered By -> @Team_X_Og ( On Telegram )
#          Updates -> @CrimeZone_Update ( On telegram )
#    
#    Setup Guides -> Read > README.md Or VPS_README.md
#    
#          This Script Part Off https://Team_X_Og's Team.
#          Copyright ©️ 2026 TeamDev | @Team_X_Og
#          
#    • Some Quick Help
#    - Use In Vps Other Way This Bot Won't Work.
#    - If You Need Any Help Contact Us In @Team_X_Og's Group
#    
#         Compatible In BotApi 9.5 Fully
#         Build For BotApi 9.4
#         We'll Keep Update This Repo If We Got 50+ Stars In One Month Of Release.


echo "TeamDev Host Bot - Setup Script"
echo "================================================"
echo ""

if [ "$EUID" -ne 0 ]; then 
    echo "⚠️  Please run as root (use sudo)"
    exit 1
fi

echo "📦 Updating system packages..."
apt-get update -y
apt-get upgrade -y

echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    systemctl enable docker
    systemctl start docker
    echo "✅ Docker installed successfully"
else
    echo "✅ Docker already installed"
fi

echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    apt-get install docker-compose -y
    echo "✅ Docker Compose installed successfully"
else
    echo "✅ Docker Compose already installed"
fi

echo "📥 Installing Git..."
if ! command -v git &> /dev/null; then
    apt-get install git -y
    echo "✅ Git installed successfully"
else
    echo "✅ Git already installed"
fi

echo "🐍 Installing Python..."
apt-get install python3 python3-pip -y

if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    
    echo ""
    echo "⚙️  Please configure your .env file:"
    echo "1. Add your BOT_TOKEN from @BotFather"
    echo "2. Add your OWNER_ID from @userinfobot"
    echo "3. Add LOG_CHANNEL_ID (optional)"
    echo ""
    read -p "Press Enter to edit .env file now..."
    nano .env
else
    echo "✅ .env file already exists"
fi

echo "📁 Creating directories..."
mkdir -p logs

echo "🔐 Setting permissions..."
chmod +x bot.py
chmod 600 .env

echo "👥 Adding user to docker group..."
usermod -aG docker $SUDO_USER

echo "🚀 Building and starting containers..."
docker-compose up -d --build

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Check status:"
echo "   docker-compose ps"
echo ""
echo "📋 View logs:"
echo "   docker-compose logs -f bot"
echo ""
echo "🛑 Stop bot:"
echo "   docker-compose down"
echo ""
echo "🔄 Restart bot:"
echo "   docker-compose restart bot"
echo ""
echo "📞 Support: @TEAM_X_OG"
echo "📢 Updates: @CrimeZone_Update"
echo "👨‍💻 Developer: @MR_ARMAN_08"
echo ""
echo "⚠️  IMPORTANT: If you edited .env just now, restart the bot:"
echo "   docker-compose restart bot"
echo ""
