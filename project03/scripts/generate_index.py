#!/usr/bin/env python3
"""Auto-generate index.html for the video gallery."""

import argparse
import glob
import os

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Project 3 — Generated Videos</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      background: #1a1a2e;
      color: #eee;
      padding: 40px;
      max-width: 1200px;
      margin: 0 auto;
    }}
    h1 {{
      color: #e94560;
      margin-bottom: 8px;
    }}
    .subtitle {{
      color: #888;
      font-size: 16px;
      margin-bottom: 30px;
    }}
    .stats {{
      background: #16213e;
      border-radius: 8px;
      padding: 16px 20px;
      margin-bottom: 30px;
      font-size: 14px;
      color: #aaa;
    }}
    .video-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(480px, 1fr));
      gap: 24px;
    }}
    .video-card {{
      background: #16213e;
      border-radius: 12px;
      padding: 16px;
      transition: transform 0.15s;
    }}
    .video-card:hover {{
      transform: translateY(-2px);
    }}
    video {{
      width: 100%;
      border-radius: 8px;
      background: #000;
      max-height: 360px;
    }}
    .filename {{
      font-size: 13px;
      color: #888;
      margin-top: 10px;
      word-break: break-all;
    }}
    .actions {{
      margin-top: 8px;
      font-size: 12px;
    }}
    .actions a {{
      color: #e94560;
      text-decoration: none;
      margin-right: 12px;
    }}
    .actions a:hover {{
      text-decoration: underline;
    }}
    .empty {{
      color: #666;
      font-style: italic;
      padding: 40px 0;
    }}
    .footer {{
      margin-top: 50px;
      padding-top: 20px;
      border-top: 1px solid #333;
      font-size: 12px;
      color: #555;
    }}
  </style>
</head>
<body>
  <h1>🎬 Project 3 — Generated Educational Videos</h1>
  <div class="subtitle">Placeholder pipeline output. Swap avatar + voice for real deployment.</div>

  <div class="stats">
    📁 {video_count} video(s) | 🖥️ Slide renderer: Chromium headless | 🎙️ TTS: edge-tts | 🎭 Avatar: LivePortrait
  </div>

  {video_grid}

  <div class="footer">
    Generated automatically by pipeline.py | Prof. Dr. Uwe Hahne @ Hochschule Furtwangen
  </div>
</body>
</html>
"""

VIDEO_CARD = """
<div class="video-card">
  <video controls preload="metadata" poster="">
    <source src="{filename}" type="video/mp4">
    Your browser does not support HTML5 video.
  </video>
  <div class="filename">{filename}</div>
  <div class="actions">
    <a href="{filename}" download>⬇️ Download</a>
    <a href="{filename}" target="_blank">🔍 Open</a>
  </div>
</div>
"""


def generate_index(root_dir):
    root_dir = os.path.abspath(root_dir)
    videos = sorted(glob.glob(os.path.join(root_dir, "*.mp4")))
    video_names = [os.path.basename(v) for v in videos]

    if not video_names:
        grid_html = '<p class="empty">No videos yet. Run pipeline.py to generate some.</p>'
    else:
        cards = "\n".join(VIDEO_CARD.format(filename=n) for n in video_names)
        grid_html = f'<div class="video-grid">\n{cards}\n</div>'

    html = HTML_TEMPLATE.format(video_count=len(video_names), video_grid=grid_html)

    index_path = os.path.join(root_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[index] {len(video_names)} video(s) — wrote {index_path}")
    return index_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/opt/data/project03-workspace/assets/output", help="Directory containing MP4 files")
    args = parser.parse_args()
    generate_index(args.root)


if __name__ == "__main__":
    main()
