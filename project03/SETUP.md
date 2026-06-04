# Project 3 — Setup & Installation Guide

Complete instructions to reproduce the working placeholder pipeline from scratch.

## Prerequisites

- Ubuntu/Debian-based Linux (tested on Debian 13)
- NVIDIA GPU with CUDA support (tested on RTX A6000, 48 GB)
- `curl`, `git`, `ffmpeg` installed
- `uv` for Python version management (https://github.com/astral-sh/uv)

## 1. Python 3.10 Installation

The system Python is 3.13 which is incompatible with pinned LivePortrait dependencies.
Install Python 3.10 via `uv` (no sudo required):

```bash
uv python install 3.10.14
export PATH="$HOME/.local/bin:$PATH"
```

## 2. Virtual Environment Setup

```bash
python3.10 -m venv venvs/lp-env
source venvs/lp-env/bin/activate
pip install --upgrade pip
```

## 3. LivePortrait Installation

```bash
git clone https://github.com/KwaiVGI/LivePortrait.git
pip install -r LivePortrait/requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 4. Download Pretrained Weights

```bash
cd LivePortrait
pip install huggingface-hub
huggingface-cli download KwaiVGI/LivePortrait \
  --local-dir pretrained_weights \
  --exclude '*.git*' 'README.md' 'README_zh_cn.md'
```

## 5. Install Additional Tools

```bash
# Placeholder TTS
pip install edge-tts

# Slide rendering (uses Hermes built-in chromium, or install playwright)
pip install playwright
playwright install chromium
```

## 6. Verify Installation

```bash
python -c "import torch, onnxruntime, cv2; print('PyTorch:', torch.__version__); print('CUDA:', torch.cuda.is_available())"
```

Expected: `torch` shows `+cu118`, `torch.cuda.is_available()` returns `True`.

## 7. Start the Gallery Server

```bash
./scripts/start_server.sh
```

Serves `assets/output/` on `http://localhost:8888/` with auto-generated video gallery.

## 8. (Optional) Public Tunnel

```bash
./scripts/start_tunnel.sh
```

Creates a Cloudflare Quick Tunnel with a random HTTPS URL.

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `libcudnn.so.8` not found | Missing cuDNN v8 for ONNXRuntime GPU | ONNX face detection falls back to CPU — output quality unaffected, just slower |
| `ModuleNotFoundError` for `PIL` | Pillow version mismatch | `pip install --force-reinstall pillow==10.4.0` |
| Chrome headless not found | Playwright/Chromium not installed | Use `chrome-headless-shell` path from Hermes at `/opt/hermes/.playwright/...` |
| Black output boxes | FP16 incompatible GPU | Set `flag_use_half_precision: false` in LivePortrait args |

---

## Files Overview

| File | Purpose |
|------|---------|
| `scripts/pipeline.py` | Main pipeline: slide → TTS → avatar → composition |
| `scripts/generate_index.py` | Auto-generates HTML gallery index |
| `scripts/start_server.sh` | Starts HTTP server on port 8888 |
| `scripts/start_tunnel.sh` | Starts Cloudflare tunnel for public access |
| `README.md` | Project overview and quick-start |
| `SETUP.md` | This file — complete reproduction guide |
