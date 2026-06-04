#!/usr/bin/env python3
"""
Project 3 — Placeholder Educational Video Pipeline
Generates slide-style educational videos with a placeholder avatar,
placeholder TTS voice, and slide background.

When real APIs are available, swap:
  - VOICE_AGENT_URL → real Voice Agent /speak endpoint
  - AVATAR_IMAGE_PATH → real Prof. Hahne avatar from Image Agent
  - LIP_SYNC_ENGINE → Wav2Lip or similar for audio-driven lips

Usage:
    source /opt/data/project03-workspace/venvs/lp-env/bin/activate
    python pipeline.py \
        --topic "Neural Radiance Fields" \
        --subtitle "Project 3 — GenAI Educational Media" \
        --text "NeRF enables photorealistic 3D scene reconstruction..." \
        --output /opt/data/project03-workspace/assets/output/video.mp4
"""

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# ─── cuDNN GPU Compatibility Fix ──────────────────────────────────────────────
# This container has cuDNN 9.x (for PyTorch) but ONNX Runtime 1.18 needs cuDNN 8.x.
# We keep both versions side-by-side and prepend LD_LIBRARY_PATH so ORT links correctly.
CUDNN8_COMPAT = "/opt/data/project03-workspace/cudnn8_compat"
CUDNN9_PKG = "/opt/data/project03-workspace/venvs/lp-env/lib/python3.10/site-packages/nvidia/cudnn/lib"

os.environ["LD_LIBRARY_PATH"] = f"{CUDNN8_COMPAT}:{CUDNN9_PKG}:{os.environ.get('LD_LIBRARY_PATH', '')}"

# ─── Configuration ────────────────────────────────────────────────────────────
CHROME_HEADLESS = "/opt/hermes/.playwright/chromium_headless_shell-1217/chrome-headless-shell-linux64/chrome-headless-shell"
LIVEPORTRAIT_DIR = "/opt/data/project03-workspace/LivePortrait"
PRETRAINED_WEIGHTS = "/opt/data/project03-workspace/LivePortrait/pretrained_weights"
PLACEHOLDER_FACE = "/opt/data/project03-workspace/assets/avatars/placeholder_face.jpg"
DRIVING_VIDEO = "/opt/data/project03-workspace/LivePortrait/assets/examples/driving/d0.mp4"
WORKSPACE = "/opt/data/project03-workspace/assets/output"

# ─── Slide HTML Template ───────────────────────────────────────────────────
SLIDE_TEMPLATE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body{{margin:0;width:1920px;height:1080px;background:#1a1a2e;
  display:flex;align-items:center;justify-content:center;
  font-family:'Segoe UI',sans-serif;}}
.slide{{width:100%;height:100%;padding:80px;box-sizing:border-box;color:#eee;}}
h1{{font-size:64px;color:#e94560;margin-bottom:40px;}}
h2{{font-size:36px;color:#0f3460;background:#e94560;padding:12px 24px;
  display:inline-block;margin-bottom:30px;}}
p{{font-size:28px;line-height:1.6;max-width:80%;}}
.footer{{position:absolute;bottom:30px;right:40px;font-size:16px;color:#888;}}
</style></head>
<body>
<div class="slide">
  <h2>{subtitle}</h2>
  <h1>{topic}</h1>
  <p>{text}</p>
  <div class="footer">Prof. Dr. Uwe Hahne | Hochschule Furtwangen</div>
</div>
</body></html>"""


def run(cmd, cwd=None, check=True):
    """Run shell command and print output."""
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def generate_slide(topic, subtitle, text, out_png):
    """Render a Reveal.js-style slide to PNG via headless Chrome."""
    html = SLIDE_TEMPLATE.format(topic=topic, subtitle=subtitle, text=text)
    html_path = out_png.replace(".png", ".html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html)

    run([
        CHROME_HEADLESS, "--headless", "--disable-gpu", "--no-sandbox",
        "--window-size=1920,1080", "--hide-scrollbars",
        f"--screenshot={out_png}", "--virtual-time-budget=1000",
        f"file://{html_path}"
    ])
    print(f"[OK] Slide rendered: {out_png}")


def generate_tts(text, out_mp3, voice="en-US-AriaNeural"):
    """Generate placeholder TTS audio via edge-tts (Microsoft Edge voice)."""
    run(["edge-tts", "--voice", voice, "--text", text, "--write-media", out_mp3])
    print(f"[OK] TTS audio: {out_mp3}")


def animate_avatar(source_face, driving_video, out_dir):
    """Run LivePortrait to animate the source face with driving motion."""
    # Use inference.py via subprocess
    run([
        sys.executable, "inference.py",
        "-s", source_face,
        "-d", driving_video,
        "-o", out_dir,
    ], cwd=LIVEPORTRAIT_DIR)
    # Find generated file
    base = Path(source_face).stem
    driving_base = Path(driving_video).stem
    animated = Path(out_dir) / f"{base}--{driving_base}.mp4"
    print(f"[OK] Avatar animation: {animated}")
    return str(animated)


def get_duration(path):
    """Get media duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def compose_video(slide_png, avatar_mp4, audio_mp3, output_mp4):
    """Compose slide + avatar overlay + audio into final MP4."""
    audio_dur = get_duration(audio_mp3)
    avatar_dur = get_duration(avatar_mp4)
    # Calculate loop count to cover audio
    loops = max(1, int(audio_dur / avatar_dur) + 1)
    looped_avatar = output_mp4.replace(".mp4", "_looped.mp4")

    # Loop avatar
    run([
        "ffmpeg", "-y", "-stream_loop", str(loops),
        "-i", avatar_mp4, "-c", "copy", "-t", str(audio_dur), looped_avatar
    ])

    # Compose: slide (static background) + avatar overlay + audio
    run([
        "ffmpeg", "-y",
        "-loop", "1", "-t", str(audio_dur), "-i", slide_png,
        "-i", looped_avatar,
        "-i", audio_mp3,
        "-filter_complex",
        "[1:v]scale=320:-1[scaled];[0:v][scaled]overlay=W-w-30:H-h-30[v]",
        "-map", "[v]", "-map", "2:a",
        "-t", str(audio_dur),
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "128k",
        output_mp4
    ])
    print(f"[OK] Final video: {output_mp4}")
    return output_mp4


def main():
    parser = argparse.ArgumentParser(description="Project 3 Placeholder Video Pipeline")
    parser.add_argument("--topic", required=True, help="Slide topic/title")
    parser.add_argument("--subtitle", default="Project 3 — GenAI Educational Media")
    parser.add_argument("--text", required=True, help="Body text for the slide")
    parser.add_argument("--voice", default="en-US-AriaNeural", help="edge-tts voice")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--face", default=PLACEHOLDER_FACE, help="Source face image")
    parser.add_argument("--driving", default=DRIVING_VIDEO, help="Driving motion video")
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.output) or WORKSPACE, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="p3_")

    slide_png = os.path.join(tmp_dir, "slide.png")
    audio_mp3 = os.path.join(tmp_dir, "audio.mp3")
    avatar_out = os.path.join(tmp_dir, "avatar")

    print("=" * 60)
    print("Project 3 — Placeholder Video Pipeline")
    print("=" * 60)

    print("\n[1/4] Generating slide...")
    generate_slide(args.topic, args.subtitle, args.text, slide_png)

    print("\n[2/4] Generating TTS audio...")
    generate_tts(args.text, audio_mp3, voice=args.voice)

    print("\n[3/4] Animating avatar with LivePortrait...")
    avatar_mp4 = animate_avatar(args.face, args.driving, avatar_out)

    print("\n[4/4] Composing final video...")
    compose_video(slide_png, avatar_mp4, audio_mp3, args.output)

    print("\n" + "=" * 60)
    print(f"DONE: {args.output}")
    print("=" * 60)
    print("\nPlaceholder swap guide:")
    print("  • Replace --face with real Prof. Hahne avatar (Image Agent)")
    print("  • Replace --text TTS with Voice Agent /speak endpoint")
    print("  • Add word-level timestamps + lip-sync for realistic mouth movement")

    # Auto-refresh gallery index
    index_path = os.path.join(os.path.dirname(args.output), "index.html")
    try:
        import generate_index
        generate_index.generate_index(os.path.dirname(args.output))
        print(f"\n[gallery] Updated {index_path}")
    except Exception as e:
        print(f"\n[gallery] Could not update index: {e}")

    print(f"\n[server] View at: http://localhost:8888/ (if server is running)")


if __name__ == "__main__":
    main()
