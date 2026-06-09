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
pip install edge-tts

# Slide rendering (uses Hermes built-in chromium, or install playwright)
pip install playwright
playwright install chromium
```

## 5b. Wav2Lip Installation (Lip-Sync)

```bash
git clone https://github.com/Rudrabha/Wav2Lip.git wav2lip
pip install gdown

cd wav2lip/checkpoints
gdown --folder "https://drive.google.com/drive/folders/153HLrqlBNxzZcHi17PEvP09kkAfzRshM"
mv checkpoints/* . && rmdir checkpoints 2>/dev/null || true
```

**Compatibility patches applied:**
- `audio.py`: `librosa.filters.mel(sr=..., n_fft=...)` keyword args for librosa 0.11
- `audio.py`: `librosa.load()` instead of deprecated `librosa.core.load()`
- `audio.py`: `soundfile.write()` instead of removed `librosa.output.write_wav()`
- `inference.py`: `torch.load(weights_only=False)` for PyTorch 2.7
- `inference.py`: TorchScript archive fallback handling

## 6. cuDNN 8/9 GPU Compatibility Fix

If your container already has cuDNN 9.x for PyTorch but ONNX Runtime 1.18 needs cuDNN 8.x, follow this once:

```bash
mkdir -p cudnn8_compat
pip download --only-binary=:all: --no-deps "nvidia-cudnn-cu11==8.9.6.50" -d /tmp
python -c "
import zipfile, os
whl='/tmp/nvidia_cudnn_cu11-8.9.6.50-py3-none-manylinux1_x86_64.whl'
ex='/opt/data/project03-workspace/cudnn8_compat'
zipfile.ZipFile(whl,'r').extractall(ex)
"
cp /opt/data/project03-workspace/cudnn8_compat/nvidia/cudnn/lib/*.so.8 \
   /opt/data/project03-workspace/cudnn8_compat/
```

`pipeline.py` already sets `LD_LIBRARY_PATH` automatically so both versions load correctly.

## 7. Hallo2 Installation (Optional — Production Avatar)

[Hallo2](https://github.com/fudan-generative-vision/Hallo2) is a diffusion-based audio-driven portrait animation model. It replaces the LivePortrait + Wav2Lip pipeline with a single native audio-to-avatar diffusion step, producing higher quality results with natural lip-sync.

```bash
# Clone Hallo2 (separate from project03 workspace)
git clone https://github.com/fudan-generative-vision/Hallo2.git
cd Hallo2

# Create dedicated venv (Hallo2 uses torch cu121, different from LivePortrait)
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Requirements include: torch==2.2.2+cu121, xformers, diffusers, transformers, omegaconf

# Download pretrained models (~2GB, ~40 files from HuggingFace)
huggingface-cli download fudan-generative-ai/hallo2 \
  --local-dir ./pretrained_models
```

### Hallo2 Configuration

Create an inference YAML (e.g., `hallo_full.yaml`):

```yaml
source_image: /path/to/prof_hahne_v4_512.jpg
driving_audio: /path/to/audio_16khz_mono.wav   # must be 16000 Hz, mono

weight_dtype: fp16

data:
  n_motion_frames: 2
  n_sample_frames: 16
  source_image:
    width: 512
    height: 512
  driving_audio:
    sample_rate: 16000
  export_video:
    fps: 25

inference_steps: 20    # 40 = highest quality; 20 = 2× faster, acceptable
cfg_scale: 3.5

use_mask: true
mask_rate: 0.25
use_cut: true

audio_ckpt_dir: pretrained_models/hallo2
save_path: /tmp/hallo2_output/

base_model_path: ./pretrained_models/stable-diffusion-v1-5
motion_module_path: ./pretrained_models/motion_module/mm_sd_v15_v2.ckpt

face_analysis:
  model_path: ./pretrained_models/face_analysis

wav2vec:
  model_path: ./pretrained_models/wav2vec/wav2vec2-base-960h
  features: all

audio_separator:
  model_path: ./pretrained_models/audio_separator/Kim_Vocal_2.onnx

vae:
  model_path: ./pretrained_models/sd-vae-ft-mse

face_expand_ratio: 1.2
pose_weight: 1.0
face_weight: 1.0
lip_weight: 1.0

unet_additional_kwargs:
  use_inflated_groupnorm: true
  use_motion_module: true
  use_audio_module: true
  motion_module_resolutions: [1, 2, 4, 8]
  motion_module_mid_block: true
  motion_module_type: Vanilla
  motion_module_kwargs:
    num_attention_heads: 8
    num_transformer_block: 1
    attention_block_types: ["Temporal_Self", "Temporal_Self"]
    temporal_position_encoding: true
    temporal_position_encoding_max_len: 32
    temporal_attention_dim_div: 1
  audio_attention_dim: 768
  stack_enable_blocks_name: ["up", "down", "mid"]
  stack_enable_blocks_depth: [0,1,2,3]

enable_zero_snr: true
noise_scheduler_kwargs:
  beta_start: 0.00085
  beta_end: 0.012
  beta_schedule: "linear"
  clip_sample: false
  steps_offset: 1
  prediction_type: "v_prediction"
  rescale_betas_zero_snr: true
  timestep_spacing: "trailing"

sampler: DDIM
```

### Run Hallo2 Inference

```bash
# Long audio (>60s) uses chunked inference
CUDA_VISIBLE_DEVICES=0 python scripts/inference_long.py --config ./hallo_full.yaml
```

**Output:** `merge_video.mp4` in `{save_path}/{image_stem}/merge_video.mp4`

**Speed:**
- 40 steps: ~42s per batch (~2.5–3h for 97s audio)
- 20 steps: ~21s per batch (~50min for 97s audio)

**VRAM:** ~9.7GB on RTX A6000

---

## 8. Verify GPU Acceleration

```bash
python -c "import torch, onnxruntime; print('PyTorch CUDA:', torch.cuda.is_available()); print('ORT providers:', onnxruntime.get_available_providers())"
```

Expected: `CUDA: True`, providers include `CUDAExecutionProvider`.

## 9. Start the Gallery Server

```bash
./scripts/start_server.sh
```

Serves `assets/output/` on `http://localhost:8888/` with auto-generated video gallery.

## 9. (Optional) Public Tunnel

```bash
./scripts/start_tunnel.sh
```

Creates a Cloudflare Quick Tunnel with a random HTTPS URL.

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `libcudnn.so.8` not found | cuDNN 9.x installed but ONNX Runtime 1.18 needs 8.x | Follow **Step 6** (cuDNN 8/9 compatibility fix) in this guide |
| `ModuleNotFoundError` for `PIL` | Pillow version mismatch | `pip install --force-reinstall pillow==10.4.0` |
| Chrome headless not found | Playwright/Chromium not installed | Use `chrome-headless-shell` path from Hermes at `/opt/hermes/.playwright/...` |
| Black output boxes | FP16 incompatible GPU | Set `flag_use_half_precision: false` in LivePortrait args |

---

## Files Overview

| File | Purpose |
|------|---------|
| `README.md` | Project overview and quick-start |
| `SETUP.md` | This file — complete reproduction guide |
| `docs/LOG.md` | Full build log — what was implemented and when |
| `docs/AUDIO_API.md` | Voice Agent API contract — what API we need |
| `docs/IMAGES.md` | Image/avatar API contract — what we need |
| `scripts/pipeline.py` | Main pipeline: LivePortrait + Wav2Lip (legacy) |
| `scripts/build_hallo2_presentation.py` | Hallo2 diffusion + slide composition (preferred) |
| `scripts/generate_index.py` | Auto-generates HTML gallery + per-video detail pages |
| `scripts/start_server.sh` | Starts HTTP server on port 8888 |
| `scripts/start_tunnel.sh` | Starts Cloudflare tunnel for public access |
| `presentations/videoretalking_presentation.json` | Example 5-slide presentation about VideoReTalking |
