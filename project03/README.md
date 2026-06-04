# Project 3 — Placeholder Implementation Workspace

This directory contains the working end-to-end pipeline for Project 3
(educational video generation with deepfake avatar + TTS narration).

## Quick Start

```bash
# Activate the Python 3.10 environment
source venvs/lp-env/bin/activate

# Generate a video
python scripts/pipeline.py \
  --topic "Your Topic Here" \
  --text "Narration script to synthesize and display." \
  --output assets/output/my_video.mp4
```

## Directory Overview

| Path | Purpose |
|------|---------|
| `venvs/lp-env/` | Python 3.10 virtualenv with LivePortrait, PyTorch, edge-tts, FFmpeg bindings |
| `LivePortrait/` | Cloned deepfake engine + pretrained weights from HuggingFace |
| `assets/avatars/` | Face images (currently placeholder; swap for Prof. Hahne) |
| `assets/audio/` | Generated TTS audio files |
| `assets/slides/` | HTML slide sources + rendered PNGs (1920×1080) |
| `assets/output/` | Final composed MP4 videos |
| `scripts/pipeline.py` | Automated 4-step pipeline script |
| `docs/` | Local API contract notes and scratchpad |

## Placeholder Swap Checklist

- [ ] **Avatar:** Replace `assets/avatars/placeholder_face.jpg` with Prof. Hahne likeness from Image Agent
- [ ] **Voice:** Replace `edge-tts` step in `pipeline.py` with Voice Agent `POST /speak`
- [ ] **Lip-sync:** Switch from pre-canned driving video to audio-driven animation (Wav2Lip or audio-conditioned LivePortrait)
- [ ] **Multi-slide:** Extend pipeline to accept slide decks instead of single topic/text

## Technical Notes

- **GPU:** RTX A6000 (48 GB) — PyTorch models run on GPU; ONNX face detector falls back to CPU due to missing `libcudnn.so.8`
- **Chromium:** Uses Hermes' built-in `chrome-headless-shell` for slide rendering
- **Python:** 3.10.14 installed via `uv` (no sudo required)
