#!/usr/bin/env python3
"""Auto-generate index.html + per-video detail pages for the gallery."""

import argparse
import glob
import json
import os
from pathlib import Path

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
      max-width: 1400px;
      margin: 0 auto;
    }}
    h1 {{ color: #e94560; margin-bottom: 8px; }}
    .subtitle {{ color: #888; font-size: 16px; margin-bottom: 30px; }}
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
      cursor: pointer;
      text-decoration: none;
      color: inherit;
      display: block;
    }}
    .video-card:hover {{ transform: translateY(-2px); }}
    video {{
      width: 100%;
      border-radius: 8px;
      background: #000;
      max-height: 360px;
    }}
    .meta {{
      margin-top: 12px;
    }}
    .meta .title {{
      font-size: 15px;
      font-weight: 600;
      color: #fff;
      margin-bottom: 4px;
    }}
    .meta .info {{
      font-size: 12px;
      color: #888;
    }}
    .meta .info span {{
      display: inline-block;
      background: #0f3460;
      padding: 2px 8px;
      border-radius: 4px;
      margin-right: 6px;
      margin-top: 4px;
    }}
    .filename {{
      font-size: 12px;
      color: #666;
      margin-top: 8px;
      word-break: break-all;
    }}
    .actions {{
      margin-top: 10px;
      font-size: 12px;
    }}
    .actions a {{
      color: #e94560;
      text-decoration: none;
      margin-right: 12px;
    }}
    .actions a:hover {{ text-decoration: underline; }}
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
<a class="video-card" href="detail/{detail_name}.html">
  <video controls preload="metadata" poster="">
    <source src="{filename}" type="video/mp4">
    Your browser does not support HTML5 video.
  </video>
  <div class="meta">
    <div class="title">{title}</div>
    <div class="info">
      <span>🎙️ {voice}</span>
      <span>📄 {slides} slide(s)</span>
      <span>⏱️ {duration}</span>
      <span>🕒 {timestamp}</span>
    </div>
  </div>
  <div class="filename">{filename}</div>
  <div class="actions">
    <a href="{filename}" download onclick="event.stopPropagation()">⬇️ Download</a>
    <a href="{filename}" target="_blank" onclick="event.stopPropagation()">🔍 Open</a>
    <a href="detail/{detail_name}.html" onclick="event.stopPropagation()">📋 Details</a>
  </div>
</a>
"""

DETAIL_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>{title} — Project 3</title>
  <style>
    body {{
      font-family: 'Segoe UI', sans-serif;
      background: #1a1a2e;
      color: #eee;
      padding: 40px;
      max-width: 1000px;
      margin: 0 auto;
    }}
    a.back {{ color: #e94560; text-decoration: none; font-size: 14px; }}
    a.back:hover {{ text-decoration: underline; }}
    h1 {{ color: #e94560; margin: 20px 0 8px; }}
    .subtitle {{ color: #888; font-size: 16px; margin-bottom: 20px; }}
    .badge {{
      display: inline-block;
      background: #0f3460;
      padding: 4px 10px;
      border-radius: 4px;
      font-size: 12px;
      color: #aaa;
      margin-right: 6px;
      margin-bottom: 6px;
    }}
    video {{
      width: 100%;
      border-radius: 12px;
      background: #000;
      margin: 20px 0;
    }}
    .section {{
      background: #16213e;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 20px;
    }}
    .section h2 {{
      font-size: 18px;
      color: #e94560;
      margin-top: 0;
      margin-bottom: 12px;
    }}
    .slide-list {{
      list-style: none;
      padding: 0;
      margin: 0;
    }}
    .slide-item {{
      background: #1a1a2e;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 10px;
      border-left: 3px solid #e94560;
    }}
    .slide-item .num {{
      font-size: 12px;
      color: #e94560;
      font-weight: bold;
      margin-bottom: 4px;
    }}
    .slide-item .topic {{
      font-size: 15px;
      font-weight: 600;
      color: #fff;
      margin-bottom: 4px;
    }}
    .slide-item .text {{
      font-size: 13px;
      color: #aaa;
      line-height: 1.5;
    }}
    .raw-meta {{
      font-family: 'Fira Code', monospace;
      font-size: 12px;
      background: #0d0d1a;
      padding: 14px;
      border-radius: 6px;
      color: #888;
      overflow-x: auto;
    }}
    .actions {{
      margin-top: 20px;
    }}
    .actions a {{
      display: inline-block;
      background: #e94560;
      color: #fff;
      text-decoration: none;
      padding: 8px 16px;
      border-radius: 6px;
      font-size: 13px;
      margin-right: 10px;
    }}
    .actions a:hover {{ background: #c0394b; }}
    .footer {{
      margin-top: 40px;
      padding-top: 20px;
      border-top: 1px solid #333;
      font-size: 12px;
      color: #555;
    }}
  </style>
</head>
<body>
  <a class="back" href="../index.html">← Back to Gallery</a>
  <h1>{title}</h1>
  <div class="subtitle">{subtitle}</div>
  <div>
    {badges}
  </div>

  <video controls preload="metadata">
    <source src="../{filename}" type="video/mp4">
    Your browser does not support HTML5 video.
  </video>

  <div class="section">
    <h2>🖥️ Slides</h2>
    <ul class="slide-list">
      {slide_list}
    </ul>
  </div>

  <div class="section">
    <h2>🎙️ Voice</h2>
    <p style="margin:0; font-size:14px; color:#aaa;">{voice}</p>
  </div>

  <div class="section">
    <h2>📦 Raw Metadata</h2>
    <pre class="raw-meta">{raw_json}</pre>
  </div>

  <div class="actions">
    <a href="../{filename}" download>⬇️ Download Video</a>
    <a href="../index.html">← Back to Gallery</a>
  </div>

  <div class="footer">
    Generated by Project 3 pipeline | Prof. Dr. Uwe Hahne @ Hochschule Furtwangen
  </div>
</body>
</html>
"""

SLIDE_ITEM = """
<li class="slide-item">
  <div class="num">Slide {num}</div>
  <div class="topic">{topic}</div>
  <div class="text">{text}</div>
</li>
"""


def load_manifest(root_dir, video_name):
    """Load JSON manifest for a video if it exists."""
    base = Path(video_name).stem
    manifest_path = Path(root_dir) / f"{base}.json"
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def generate_index(root_dir):
    root_dir = os.path.abspath(root_dir)
    videos = sorted(glob.glob(os.path.join(root_dir, "*.mp4")))
    video_names = [os.path.basename(v) for v in videos]

    # Filter: skip looped intermediates and videos without a manifest
    video_names = [
        name for name in video_names
        if not name.endswith("_looped.mp4") and load_manifest(root_dir, name)
    ]

    if not video_names:
        grid_html = '<p class="empty">No videos yet. Run pipeline.py to generate some.</p>'
    else:
        cards = []
        for name in video_names:
            manifest = load_manifest(root_dir, name)
            detail_name = Path(name).stem

            title = manifest.get("topic", detail_name)
            voice = manifest.get("voice", "en-US-AriaNeural").split("-")[-1]  # short name
            slides = len(manifest.get("slides", []))
            if slides == 0:
                slides = 1
            duration = manifest.get("duration", "N/A")
            timestamp = manifest.get("timestamp", "")
            if timestamp:
                timestamp = timestamp.replace("T", " ").split(".")[0]

            cards.append(VIDEO_CARD.format(
                filename=name,
                detail_name=detail_name,
                title=title,
                voice=voice,
                slides=slides,
                duration=duration,
                timestamp=timestamp
            ))
        grid_html = f'<div class="video-grid">\n{"".join(cards)}\n</div>'

    html = HTML_TEMPLATE.format(video_count=len(video_names), video_grid=grid_html)

    index_path = os.path.join(root_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"[index] {len(video_names)} video(s) — wrote {index_path}")
    return index_path


def generate_detail_pages(root_dir):
    """Generate per-video detail pages."""
    root_dir = os.path.abspath(root_dir)
    videos = sorted(glob.glob(os.path.join(root_dir, "*.mp4")))

    # Same filtering for detail pages
    videos = [
        v for v in videos
        if not os.path.basename(v).endswith("_looped.mp4")
    ]

    detail_dir = Path(root_dir) / "detail"
    detail_dir.mkdir(exist_ok=True)

    for video_path in videos:
        name = os.path.basename(video_path)
        base = Path(name).stem
        manifest = load_manifest(root_dir, name)

        if not manifest:
            continue

        title = manifest.get("topic", base)
        subtitle = manifest.get("subtitle", "")
        voice = manifest.get("voice", "en-US-AriaNeural")
        slides = manifest.get("slides", [])
        raw_json = json.dumps(manifest, indent=2)

        if slides:
            slide_items = "\n".join(
                SLIDE_ITEM.format(num=i+1, topic=s.get("topic", ""), text=s.get("text", ""))
                for i, s in enumerate(slides)
            )
        else:
            slide_items = SLIDE_ITEM.format(num=1, topic=title, text=manifest.get("text", ""))

        badges = "\n".join(
            f'<span class="badge">{b}</span>' for b in [
                f"🎙️ {voice}",
                f"📄 {len(slides) if slides else 1} slide(s)",
                f"⏱️ {manifest.get('duration', 'N/A')}",
                f"🕒 {manifest.get('timestamp', '').replace('T', ' ').split('.')[0]}"
            ]
        )

        html = DETAIL_TEMPLATE.format(
            title=title,
            subtitle=subtitle,
            badges=badges,
            filename=name,
            slide_list=slide_items,
            voice=voice,
            raw_json=raw_json
        )

        detail_path = detail_dir / f"{base}.html"
        with open(detail_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"[detail] {detail_path}")

    return str(detail_dir)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="/opt/data/project03-workspace/assets/output", help="Directory containing MP4 files")
    args = parser.parse_args()
    generate_index(args.root)
    generate_detail_pages(args.root)


if __name__ == "__main__":
    main()
