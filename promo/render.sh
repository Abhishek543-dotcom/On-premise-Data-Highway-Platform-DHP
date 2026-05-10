#!/bin/bash
# render.sh - Render the promotional video
# Outputs: media/videos/video/1080p60/FullVideo.mp4
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}/.."

echo "=== Rendering DataHarbour Promo Video ==="
echo "    Resolution: 1080x1920 (Portrait)"
echo "    Quality: High (1080p60)"
echo ""

manim render promo/video.py FullVideo -qh

echo ""
echo "=== Render complete! ==="
echo "Output: media/videos/video/1080p60/FullVideo.mp4"
echo ""
echo "Upload this file to LinkedIn as a video post."
