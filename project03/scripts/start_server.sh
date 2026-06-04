#!/usr/bin/env bash
# Start the Project 3 video gallery webserver
# Usage: ./start_server.sh [port]

PORT=${1:-8888}
ROOT="/opt/data/project03-workspace/assets/output"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Generate index.html on startup
source /opt/data/project03-workspace/venvs/lp-env/bin/activate
python "${SCRIPT_DIR}/generate_index.py" --root "$ROOT"

echo "========================================"
echo "Project 3 Video Gallery Server"
echo "========================================"
echo "Root:  $ROOT"
echo "Port:  $PORT"
echo "URL:   http://localhost:$PORT/"
echo ""
echo "Videos available:"
ls -1 "$ROOT"/*.mp4 2>/dev/null | sed 's|.*/||; s/^/  - /' || echo "  (none yet)"
echo ""
echo "Press Ctrl+C to stop"
echo "========================================"

# Serve with Python's built-in HTTP server
cd "$ROOT" && python -m http.server "$PORT" --bind 0.0.0.0
