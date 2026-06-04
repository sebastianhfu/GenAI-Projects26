#!/usr/bin/env bash
# Start Cloudflare tunnel to expose the Project 3 video gallery
# Usage: ./start_tunnel.sh [port]

PORT=${1:-8888}
TUNNEL_BIN="/tmp/cloudflared_extract/usr/bin/cloudflared"

if [ ! -f "$TUNNEL_BIN" ]; then
    echo "Cloudflared not found. Installing..."
    curl -L --output /tmp/cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
    mkdir -p /tmp/cloudflared_extract
    dpkg-deb -x /tmp/cloudflared.deb /tmp/cloudflared_extract
fi

echo "Starting Cloudflare tunnel for http://localhost:$PORT"
echo "Press Ctrl+C to stop"
echo ""

$TUNNEL_BIN tunnel --url "http://localhost:$PORT"
