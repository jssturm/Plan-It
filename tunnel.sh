#!/bin/bash
# Cloudflare Tunnel auto-reconnect wrapper — survives sleep/wake and disconnects.
# Usage: ./tunnel.sh [port]  (default: 8000)

PORT="${1:-8000}"
CLOUDFLARED="${HOME}/.local/bin/cloudflared"

if [ ! -x "$CLOUDFLARED" ]; then
    echo "cloudflared not found at $CLOUDFLARED"
    echo "Install: curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared"
    exit 1
fi

echo "🌐 Tunnel keepalive started on port $PORT"
echo "   Auto-restarts after sleep/disconnects"
echo ""

while true; do
    echo "[$(date '+%H:%M:%S')] Starting cloudflared tunnel..."
    "$CLOUDFLARED" tunnel --url "http://127.0.0.1:${PORT}" 2>&1 | while IFS= read -r line; do
        echo "$line"
        # Extract and save tunnel URL whenever it appears (handles reconnects)
        if echo "$line" | grep -q "trycloudflare.com"; then
            echo "$line" | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' > /tmp/travel_tunnel_url
        fi
    done
    echo ""
    echo "[$(date '+%H:%M:%S')] Tunnel disconnected — restarting in 5 seconds..."
    sleep 5
done