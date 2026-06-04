#!/usr/bin/env python3
"""
Project 3 — Placeholder Educational Video Pipeline
Generates slide-style educational videos with a placeholder avatar,
placeholder TTS voice, and slide background.

Supports single-slide CLI mode and multi-slide presentation mode via JSON.

Wav2Lip lip-sync is now integrated: the avatar's mouth movements
are driven by the actual TTS audio waveform.

When real APIs are available, swap:
  - VOICE_AGENT_URL → real Voice Agent /speak endpoint
  - AVATAR_IMAGE_PATH → real Prof. Hahne avatar from Image Agent
  - (Lip-sync engine stays as Wav2Lip — it works with any voice audio)

Usage (single slide):
    python pipeline.py \
        --topic "Neural Radiance Fields" \
        --subtitle "Project 3 — GenAI Educational Media" \
        --text "NeRF enables photorealistic 3D scene reconstruction..." \
        --output /opt/data/project03-workspace/assets/output/video.mp4

Usage (multi-slide presentation):
    python pipeline.py --presentation slides.json --output out.mp4
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime
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
WAV2LIP_DIR = "/opt/data/project03-workspace/wav2lip"
WAV2LIP_CHECKPOINT = "/opt/data/project03-workspace/wav2lip/checkpoints/Wav2Lip-SD-GAN.pt"
PRETRAINED_WEIGHTS = "/opt/data/project03-workspace/LivePortrait/pretrained_weights"
PLACEHOLDER_FACE = "/opt/data/project03-workspace/assets/avatars/placeholder_face.jpg"
DRIVING_VIDEO = "/opt/data/project03-workspace/LivePortrait/assets/examples/driving/d0.mp4"
WORKSPACE = "/opt/data/project03-workspace/assets/output"

# ─── Slide HTML Template ────────────────────────────────────────────────────
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
    run([
        sys.executable, "inference.py",
        "-s", source_face,
        "-d", driving_video,
        "-o", out_dir,
    ], cwd=LIVEPORTRAIT_DIR)
    base = Path(source_face).stem
    driving_base = Path(driving_video).stem
    animated = Path(out_dir) / f"{base}--{driving_base}.mp4"
    print(f"[OK] Avatar animation: {animated}")
    return str(animated)


def lip_sync_avatar(face_video, audio_file, out_video, resize_factor=1):
    """Run Wav2Lip to lip-sync the avatar video to the given audio."""
    run([
        sys.executable, "inference.py",
        "--checkpoint_path", WAV2LIP_CHECKPOINT,
        "--face", face_video,
        "--audio", audio_file,
        "--outfile", out_video,
        "--resize_factor", str(resize_factor),
    ], cwd=WAV2LIP_DIR)
    print(f"[OK] Lip-synced avatar: {out_video}")
    return out_video


def get_duration(path):
    """Get media duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())


def concat_audios(audio_files, out_wav):
    """Concatenate multiple MP3 files into one WAV via ffmpeg."""
    inputs = sum([["-i", f] for f in audio_files], [])
    n = len(audio_files)
    filter_str = "".join(f"[{i}:a]" for i in range(n)) + f"concat=n={n}:v=0:a=1[a]"
    run([
        "ffmpeg", "-y", *inputs,
        "-filter_complex", filter_str,
        "-map", "[a]",
        "-ac", "1", "-ar", "22050",
        out_wav
    ])
    return out_wav


def compose_video(slide_pngs, avatar_mp4, audio_mp3s, output_mp4):
    """Compose slides + avatar overlay + audio into final MP4."""
    # Calculate total audio duration
    total_audio_dur = sum(get_duration(a) for a in audio_mp3s)
    avatar_dur = get_duration(avatar_mp4)
    loops = max(1, int(total_audio_dur / avatar_dur) + 1)
    looped_avatar = output_mp4.replace(".mp4", "_looped.mp4")

    # Loop avatar
    run([
        "ffmpeg", "-y", "-stream_loop", str(loops),
        "-i", avatar_mp4, "-c", "copy", "-t", str(total_audio_dur), looped_avatar
    ])

    # Build complex filter for multi-slide + multi-audio
    if len(slide_pngs) == 1 and len(audio_mp3s) == 1:
        # Single slide path (fast)
        run([
            "ffmpeg", "-y",
            "-loop", "1", "-t", str(total_audio_dur), "-i", slide_pngs[0],
            "-i", looped_avatar,
            "-i", audio_mp3s[0],
            "-filter_complex",
            "[1:v]scale=320:-1[scaled];[0:v][scaled]overlay=W-w-30:H-h-30[v]",
            "-map", "[v]", "-map", "2:a",
            "-t", str(total_audio_dur),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            output_mp4
        ])
    else:
        # Multi-slide path
        inputs = []
        for png in slide_pngs:
            inputs += ["-loop", "1", "-i", png]
        for mp3 in audio_mp3s:
            inputs += ["-i", mp3]
        inputs += ["-i", looped_avatar]

        n_slides = len(slide_pngs)
        n_audios = len(audio_mp3s)

        # Build filter_complex
        filters = []
        # Scale avatar
        filters.append(f"[{n_slides + n_audios}:v]scale=320:-1[scaled]")

        # Concat slides with their durations
        slide_durs = [get_duration(a) for a in audio_mp3s]
        for i in range(n_slides):
            if i < n_slides - 1:
                filters.append(f"[{i}:v]trim=duration={slide_durs[i]}[v{i}]")
            else:
                # Last slide: extend to cover any remaining time
                remaining = total_audio_dur - sum(slide_durs[:-1])
                filters.append(f"[{i}:v]trim=duration={remaining}[v{i}]")

        # Concatenate video segments
        concat_inputs = "".join(f"[v{i}]" for i in range(n_slides))
        filters.append(f"{concat_inputs}concat=n={n_slides}:v=1:a=0[concat_v]")

        # Overlay avatar
        filters.append(f"[concat_v][scaled]overlay=W-w-30:H-h-30[final_v]")

        # Concatenate audio
        audio_inputs = "".join(f"[{n_slides + i}:a]" for i in range(n_audios))
        filters.append(f"{audio_inputs}concat=n={n_audios}:v=0:a=1[final_a]")

        filter_str = ";".join(filters)

        run([
            "ffmpeg", "-y",
            *inputs,
            "-filter_complex", filter_str,
            "-map", "[final_v]", "-map", "[final_a]",
            "-t", str(total_audio_dur),
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            output_mp4
        ])

    print(f"[OK] Final video: {output_mp4}")
    return output_mp4


def save_manifest(output_path, manifest):
    """Save JSON manifest alongside the MP4."""
    manifest_path = output_path.replace(".mp4", ".json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"[OK] Manifest: {manifest_path}")


def build_single_slide(args):
    """Build a single-slide video from CLI args."""
    os.makedirs(os.path.dirname(args.output) or WORKSPACE, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="p3_")

    slide_png = os.path.join(tmp_dir, "slide.png")
    audio_mp3 = os.path.join(tmp_dir, "audio.mp3")
    avatar_out = os.path.join(tmp_dir, "avatar")

    print("=" * 60)
    print("Project 3 — Placeholder Video Pipeline (single slide)")
    print("=" * 60)

    print("\n[1/4] Generating slide...")
    generate_slide(args.topic, args.subtitle, args.text, slide_png)

    print("\n[2/4] Generating TTS audio...")
    generate_tts(args.text, audio_mp3, voice=args.voice)

    print("\n[3/4] Animating avatar with LivePortrait...")
    avatar_mp4 = animate_avatar(args.face, args.driving, avatar_out)

    print("\n[3.5/4] Lip-syncing avatar with Wav2Lip...")
    synced_avatar = audio_mp3.replace(".mp3", "_synced.mp4")
    lip_sync_avatar(avatar_mp4, audio_mp3, synced_avatar)

    print("\n[4/4] Composing final video...")
    compose_video([slide_png], synced_avatar, [audio_mp3], args.output)

    # Save manifest
    manifest = {
        "topic": args.topic,
        "subtitle": args.subtitle,
        "text": args.text,
        "voice": args.voice,
        "face": args.face,
        "driving": args.driving,
        "duration": f"{get_duration(args.output):.1f}s",
        "timestamp": datetime.now().isoformat(),
        "slides": [{"topic": args.topic, "text": args.text}],
        "lip_sync": True,
        "lip_sync_engine": "Wav2Lip"
    }
    save_manifest(args.output, manifest)

    print("\n" + "=" * 60)
    print(f"DONE: {args.output}")
    print("=" * 60)
    print("\nPlaceholder swap guide:")
    print("  • Replace --face with real Prof. Hahne avatar (Image Agent)")
    print("  • Replace --text TTS with Voice Agent /speak endpoint")
    print("  • Add word-level timestamps + lip-sync for realistic mouth movement")

    refresh_gallery(args.output)
    return args.output


def build_presentation(args):
    """Build a multi-slide presentation from JSON input."""
    with open(args.presentation, "r", encoding="utf-8") as f:
        pres = json.load(f)

    slides = pres.get("slides", [])
    if not slides:
        raise ValueError("Presentation JSON must contain 'slides' array")

    os.makedirs(os.path.dirname(args.output) or WORKSPACE, exist_ok=True)
    tmp_dir = tempfile.mkdtemp(prefix="p3pres_")

    print("=" * 60)
    print(f"Project 3 — Presentation ({len(slides)} slides)")
    print("=" * 60)

    slide_pngs = []
    audio_mp3s = []

    for i, slide in enumerate(slides):
        topic = slide.get("topic", f"Slide {i+1}")
        subtitle = slide.get("subtitle", pres.get("subtitle", "Project 3 — GenAI Educational Media"))
        text = slide.get("text", "")
        voice = slide.get("voice", pres.get("voice", "en-US-AriaNeural"))

        print(f"\n[Slide {i+1}/{len(slides)}] {topic}")
        png = os.path.join(tmp_dir, f"slide_{i}.png")
        mp3 = os.path.join(tmp_dir, f"audio_{i}.mp3")

        generate_slide(topic, subtitle, text, png)
        generate_tts(text, mp3, voice=voice)

        slide_pngs.append(png)
        audio_mp3s.append(mp3)

    print("\n[Avatar] Animating with LivePortrait...")
    avatar_out = os.path.join(tmp_dir, "avatar")
    face = pres.get("face", args.face)
    driving = pres.get("driving", args.driving)
    avatar_mp4 = animate_avatar(face, driving, avatar_out)

    print("\n[Lip-sync] Concatenating audio + running Wav2Lip...")
    # Concatenate all MP3s into one WAV for Wav2Lip
    concat_wav = os.path.join(tmp_dir, "concat_audio.wav")
    concat_audios(audio_mp3s, concat_wav)
    synced_avatar = os.path.join(tmp_dir, "avatar_lip_synced.mp4")
    lip_sync_avatar(avatar_mp4, concat_wav, synced_avatar)

    print("\n[Composition] Building final video...")
    compose_video(slide_pngs, synced_avatar, audio_mp3s, args.output)

    # Save manifest
    manifest = {
        "topic": pres.get("title", slides[0].get("topic", "Presentation")),
        "subtitle": pres.get("subtitle", ""),
        "voice": pres.get("voice", "en-US-AriaNeural"),
        "face": face,
        "driving": driving,
        "duration": f"{get_duration(args.output):.1f}s",
        "timestamp": datetime.now().isoformat(),
        "slides": slides,
        "lip_sync": True,
        "lip_sync_engine": "Wav2Lip"
    }
    save_manifest(args.output, manifest)

    print("\n" + "=" * 60)
    print(f"DONE: {args.output}")
    print(f"Slides: {len(slides)} | Total duration: {manifest['duration']}")
    print("=" * 60)

    refresh_gallery(args.output)
    return args.output


def refresh_gallery(output_path):
    """Auto-refresh gallery index."""
    output_dir = os.path.dirname(output_path)
    index_path = os.path.join(output_dir, "index.html")
    try:
        import generate_index
        generate_index.generate_index(output_dir)
        generate_index.generate_detail_pages(output_dir)
        print(f"\n[gallery] Updated {output_dir}/index.html + detail/ pages")
    except Exception as e:
        print(f"\n[gallery] Could not update: {e}")

    print(f"\n[server] View at: http://localhost:8888/ (if server is running)")


def main():
    parser = argparse.ArgumentParser(description="Project 3 Placeholder Video Pipeline")
    parser.add_argument("--topic", help="Slide topic/title")
    parser.add_argument("--subtitle", default="Project 3 — GenAI Educational Media")
    parser.add_argument("--text", help="Body text for the slide")
    parser.add_argument("--voice", default="en-US-AriaNeural", help="edge-tts voice")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    parser.add_argument("--face", default=PLACEHOLDER_FACE, help="Source face image")
    parser.add_argument("--driving", default=DRIVING_VIDEO, help="Driving motion video")
    parser.add_argument("--presentation", help="Path to JSON presentation file (enables multi-slide mode)")
    args = parser.parse_args()

    if args.presentation:
        build_presentation(args)
    else:
        if not args.topic or not args.text:
            parser.error("--topic and --text are required (or use --presentation)")
        build_single_slide(args)


if __name__ == "__main__":
    main()
