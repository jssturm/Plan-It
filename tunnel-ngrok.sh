#!/bin/bash
# ngrok Tunnel auto-reconnect wrapper for Travel-App
# Usage: ./tunnel-ngrok.sh [port]  (default: 8000)
#
# Requires ngrok installed and authenticated (ngrok config check).
# Free tier allows 3 simultaneous tunnels.

PORT="${1:-8000}"
NGROK="${HOME}/.local/bin/ngrok"

if [ ! -x "$NGROK" ]; then
    echo "ngrok not found at $NGROK"
    echo "Install: curl -s https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null && echo 'deb https://ngrok-agent.s3.amazonaws.com buster main' | sudo tee /etc/apt/sources.list.d/ngrok.list && sudo apt update && sudo apt install ngrok"
    echo "Then authenticate: ngrok config add-authtoken <your-token>"
    exit 1
fi

# Verify auth
if ! ngrok config check 2>/dev/null | grep -q "Valid configuration"; then
    echo "ngrok not authenticated. Run: ngrok config add-authtoken <your-token>"
    echo "Get your token at: https://dashboard.ngrok.com/get-started/your-authtoken"
    exit 1
fi

echo "🌐 ngrok tunnel keepalive started on port $PORT"
echo "   Auto-restarts after disconnects"
echo "   Free tier: up to 3 simultaneous tunnels"
echo ""

# Write tunnel URL to a file so it's easy to find/share
URL_FILE="/tmp/travel_ngrok_url"

while true; do
    echo "[$(date '+%H:%M:%S')] Starting ngrok tunnel..."
    "$NGROK" http --url=http://127.0.0.1:${PORT} \
        --log=stdout \
        --log-format=json \
        2>&1 | while IFS= read -r line; do
        echo "$line"
        # Extract and save tunnel URL from JSON log output
        if echo "$line" | python3 -c "
import sys, json
try:
    data = json.loads(sys.stdin.read())
    if data.get('obj') == 'url' and data.get('addr') and 'trycloudflare' not in data.get('addr',''):
        url = data.get('addr','')
        if url:
            with open('$URL_FILE', 'w') as f:
                f.write(url + '\n')
except:
    pass
" 2>/dev/null; then
            if [ -f "$URL_FILE" ]; then
                echo "   ✅ Tunnel URL: $(cat $URL_FILE)"
            fi
        fi
    done
    echo ""
    echo "[$(date '+%H:%M:%S')] Tunnel disconnected — restarting in 5 seconds..."
    sleep 5
done