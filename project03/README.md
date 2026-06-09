# Project 3 — GenAI Educational Media Pipeline

> **Status:** 🟢 Operational — Real avatar (Prof. Hahne) integrated. Hallo2 diffusion pipeline producing production-quality output.
> **Institution:** Hochschule Furtwangen (HFU), Faculty I: Computer Science & Applications
> **Project Lead:** Prof. Dr. Uwe Hahne

---

## What is This?

An automated pipeline that generates educational lecture videos with a **deepfake avatar of Prof. Dr. Uwe Hahne**, **TTS narration**, and **slide overlays**. Designed for GenAI research and the Industrial Metaverse at HFU.

**Live gallery:** [https://saved-carter-auditor-wanted.trycloudflare.com](https://saved-carter-auditor-wanted.trycloudflare.com) *(ephemeral tunnel — may rotate)*

---

## Architecture

```
┌──────────────┐    ┌──────────────────────────────────────────────────┐
│   TTS Audio  │───→│ LivePortrait (pose-only) + Wav2Lip lip-sync     │  ← v4–v8
│  (edge-tts)  │    └──────────────────────────────────────────────────┘
└──────────────┘    ┌──────────────────────────────────────────────────┐
                    │ Hallo2 (audio-driven diffusion, native lip-sync)   │  ← v9+ ✅
                    └──────────────────────────────────────────────────┘
                                                                  ↓
                                                          FFmpeg Compose
                                                                 ↑
                                                      Slides (Chromium)
```

**Pipeline stages:**
1. **Slide rendering** — Chromium headless renders HTML slides to 1920×1080 PNG
2. **TTS generation** — `edge-tts` (Microsoft Edge neural voice, no API key needed)
3. **Avatar generation** — **Hallo2** (audio-guided diffusion, native lip-sync + natural head motion)
4. **Composition** — FFmpeg overlays 350px avatar on slides + burns HFU logo + mixes audio
5. **Gallery** — Auto-generated `index.html` with per-video detail pages

---

## Generated Versions

| Version | Approach | Duration | Quality | Status |
|---------|----------|----------|---------|--------|
| v4–v6 | LivePortrait (expression) + Wav2Lip | 97s | Mouth wildly flapping, extreme motion | ❌ |
| v7 | LivePortrait (`--animation-region pose`) + Wav2Lip | 97s | Too static, no eye movement, blurry lips | ⚠️ |
| v8 | LivePortrait (`d0.mp4` natural idle) + Wav2Lip-SD-NOGAN | 97s | Good idle motion, sharper lips | ✅ |
| **v9 (Hallo2)** | **Hallo2 diffusion (20 steps, audio-driven)** | **97s** | **Best: natural motion + native lip-sync** | **✅ Preferred** |

---

## Quick Start

```bash
# Activate environment
source venvs/lp-env/bin/activate

# LivePortrait + Wav2Lip pipeline (legacy, v4–v8)
python scripts/pipeline.py \
  --presentation presentations/videoretalking_presentation.json \
  --output assets/output/videoretalking_presentation_v8.mp4

# Hallo2 diffusion pipeline (preferred, v9+)
# 1. Generate slide audio (TTS) → hallo_full.yaml → inference
# 2. Run scripts/build_hallo2_presentation.py
```

See [**SETUP.md**](SETUP.md) for full environment reproduction including Hallo2 install.

---

## Documentation

| Page | Description |
|------|-------------|
| [**LOG →**](docs/LOG.md) | Full build log — what was implemented and when |
| [**AUDIO API →**](docs/AUDIO_API.md) | Voice Agent integration spec |
| [**IMAGES →**](docs/IMAGES.md) | Avatar / Image Agent integration spec |
| [**SETUP.md**](SETUP.md) | Complete reproduction guide (LivePortrait + Wav2Lip + Hallo2) |

---

## Current State

| Component | Status | Notes |
|-----------|--------|-------|
| **Avatar** | ✅ Real photo (`prof_hahne_v4_512.jpg`) | HFU profile photo, 512×512 |
| **Voice** | ✅ `edge-tts` | en-US-AriaNeural — natural, no API key |
| **Head motion** | ✅ Hallo2 diffusion | Natural idle + blinks, audio-conditioned |
| **Lip-sync** | ✅ Native Hallo2 | No separate Wav2Lip needed |
| **Gallery** | ✅ Auto-generated | Cache-busting headers, detail pages |
| **HFU branding** | ✅ Logo overlay | Top-right corner on all outputs |

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Avatar engine | **Hallo2** (diffusion, audio-guided) |
| Legacy avatar | LivePortrait + Wav2Lip-SD-NOGAN |
| TTS | edge-tts (Microsoft Edge neural) |
| Slide renderer | Chromium headless (1920×1080) |
| Video composer | FFmpeg (overlay, concat, logo burn) |
| GPU | NVIDIA RTX A6000 (48 GB) |
| Python | 3.10.14 (via `uv`) |
| Gallery | Auto-generated static HTML with cache-busting |

---

## Directory Overview

```
project03/
├── README.md              ← You are here
├── SETUP.md               ← Full reproduction guide
├── docs/
│   ├── LOG.md             ← Build history
│   ├── AUDIO_API.md       ← Voice API contract
│   └── IMAGES.md          ← Image/avatar API contract
├── scripts/
│   ├── pipeline.py              ← LivePortrait + Wav2Lip pipeline
│   ├── build_hallo2_presentation.py  ← Hallo2 + slide composition
│   ├── generate_index.py        ← Gallery + detail page generator
│   ├── start_server.sh          ← Local gallery server
│   └── start_tunnel.sh          ← Cloudflare tunnel
├── presentations/
│   └── videoretalking_presentation.json
├── assets/
│   ├── avatars/           ← prof_hahne_v4_512.jpg
│   ├── audio/             ← TTS outputs
│   ├── slides/            ← HTML sources + rendered PNGs
│   └── output/            ← Final MP4s + gallery index
├── LivePortrait/          ← Deepfake engine + weights
├── wav2lip/               ← Lip-sync engine + checkpoints
└── Hallo2/                ← Diffusion avatar engine (external)
```

---

## Gallery

The pipeline auto-generates:
- **`index.html`** — dark-mode gallery with video cards + cache-busting meta tags
- **`detail/{video}.html`** — per-video pages showing slide list, voice used, metadata, raw JSON
- **Filter rules** — skips `_looped.mp4` intermediates, skips videos without JSON manifests

Gallery server runs on port 8888.

---

*Prof. Dr. Uwe Hahne @ Hochschule Furtwangen | GenAI Educational Media Project*
