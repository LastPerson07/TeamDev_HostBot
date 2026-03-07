#!/bin/bash

VPS_USER="${VPS_USER:-vpsuser}"
VPS_PASSWORD="${VPS_PASSWORD:-changeme123}"
VPS_TIER="${VPS_TIER:-Free}"
VPS_EXPIRES="${VPS_EXPIRES:-24 Hours}"

HASHED=$(openssl passwd -6 "${VPS_PASSWORD}")
usermod -p "${HASHED}" "${VPS_USER}"

echo "${VPS_USER} ALL=(ALL) !ALL" >> /etc/sudoers 2>/dev/null || true

cat > /home/${VPS_USER}/.bashrc << BASHRCEOF
clear

echo "  ████████╗███████╗ █████╗ ███╗   ███╗██████╗ ███████╗██╗   ██╗"
echo "  ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██╔══██╗██╔════╝██║   ██║"
echo "     ██║   █████╗  ███████║██╔████╔██║██║  ██║█████╗  ██║   ██║"
echo "     ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║██║  ██║██╔══╝  ╚██╗ ██╔╝"
echo "     ██║   ███████╗██║  ██║██║ ╚═╝ ██║██████╔╝███████╗ ╚████╔╝ "
echo "     ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚══════╝  ╚═══╝ "
echo ""
echo "           ⚡  Powered by \$TeamDev VPS Platform  ⚡"
echo ""
echo "  ╔══════════════════════════════════════════════════════╗"
echo "  ║        🖥️   WELCOME TO YOUR MINI VPS               ║"
echo "  ╠══════════════════════════════════════════════════════╣"
echo "  ║  ● Status   │ Online & Running                      ║"
echo "  ║  ● Tier     │ ${VPS_TIER}                           ║"
echo "  ║  ● Expires  │ ${VPS_EXPIRES}                        ║"
echo "  ║  ● User     │ \$(whoami)                             ║"
echo "  ╠══════════════════════════════════════════════════════╣"
echo "  ║  ✓ Python3  ✗ Sudo   ✓ Git    ✓ Node.js            ║"
echo "  ║  ✓ Nano     ✓ Vim    ✓ Screen ✓ Tmux               ║"
echo "  ╠══════════════════════════════════════════════════════╣"
echo "  ║  📢 Support │ t.me/Team_x_Og                        ║"
echo "  ║  📣 Updates │ t.me/CrimeZone_Update                 ║"
echo "  ║  👨‍💻 Dev     │ t.me/MR_ARMAN_08                      ║"
echo "  ║  🤖 Bot     │ t.me/TeamDev_HostBot                  ║"
echo "  ╚══════════════════════════════════════════════════════╝"
echo ""
echo "  Type help-vps to see available commands"
echo ""

# Simple clean prompt — no color escape issues
export PS1='[vps@TeamDev-VPS \w]\$ '

alias ll='ls -la --color=auto'
alias ls='ls --color=auto'
alias py='python3'
alias pip='pip3'
alias c='clear'
alias ..='cd ..'
alias ports='ss -tlnp'
alias myip='curl -s ifconfig.me && echo'
alias usage='df -h && echo "" && free -h'

help-vps() {
    echo ""
    echo "  ╔══════════════════════════════════════╗"
    echo "  ║      📖 VPS Quick Commands           ║"
    echo "  ╠══════════════════════════════════════╣"
    echo "  ║  py        → python3                 ║"
    echo "  ║  pip       → pip3                    ║"
    echo "  ║  ll        → ls -la                  ║"
    echo "  ║  myip      → show public IP          ║"
    echo "  ║  usage     → disk & ram usage        ║"
    echo "  ║  ports     → show open ports         ║"
    echo "  ║  c         → clear screen            ║"
    echo "  ╚══════════════════════════════════════╝"
    echo ""
}
export -f help-vps
BASHRCEOF

chown ${VPS_USER}:${VPS_USER} /home/${VPS_USER}/.bashrc
truncate -s 0 /etc/motd

echo "[TeamDev] VPS Ready — User: ${VPS_USER} | Tier: ${VPS_TIER}"
exec /usr/sbin/sshd -D
