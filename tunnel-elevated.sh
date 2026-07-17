#!/bin/bash
# Cloudflare Tunnel auto-reconnect wrapper for Elevated-Applicant
# Usage: ./tunnel-elevated.sh [port]  (default: 3000)
#
# Survives sleep/wake cycles and network disconnects.

PORT="${1:-3000}"
CLOUDFLARED="${HOME}/.local/bin/cloudflared"
URL_FILE="/tmp/elevated_tunnel_url"

if [ ! -x "$CLOUDFLARED" ]; then
    echo "cloudflared not found at $CLOUDFLARED"
    echo "Install: curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o ~/.local/bin/cloudflared && chmod +x ~/.local/bin/cloudflared"
    exit 1
fi

echo "🌐 Elevated-Applicant tunnel keepalive started on port $PORT   [$(date '+%Y-%m-%d %H:%M:%S')]"
echo "   Auto-restarts after sleep/disconnects"
echo "   URL saved to: $URL_FILE"
echo ""

while true; do
    echo "[$(date '+%H:%M:%S')] Starting cloudflared tunnel for Elevated-Applicant..."
    "$CLOUDFLARED" tunnel --url "http://127.0.0.1:${PORT}" 2>&1 | while IFS= read -r line; do
        echo "$line"
        # Extract and save tunnel URL whenever it appears (handles reconnects)
        if echo "$line" | grep -q "trycloudflare.com"; then
            echo "$line" | grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' > "$URL_FILE" 2>/dev/null
            if [ -s "$URL_FILE" ]; then
                echo "   ✅ Elevated-Applicant URL: $(cat $URL_FILE)"
            fi
        fi
    done
    echo ""
    echo "[$(date '+%H:%M:%S')] Elevated-Applicant tunnel disconnected — restarting in 5 seconds..."
    sleep 5
done