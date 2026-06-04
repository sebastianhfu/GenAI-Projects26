# Project 3 — GenAI Educational Media Pipeline

> **Status:** 🟢 Active — Pipeline operational with placeholder components. Awaiting real avatar + voice APIs for production swap.
> **Institution:** Hochschule Furtwangen (HFU), Faculty I: Computer Science & Applications
> **Project Lead:** Prof. Dr. Uwe Hahne

---

## What is This?

An automated pipeline that generates educational lecture videos with a **deepfake avatar**, **TTS narration**, and **slide overlays**. Designed for Prof. Hahne's GenAI research at HFU.

**Live preview:** [https://herb-queries-clearly-seafood.trycloudflare.com](https://herb-queries-clearly-seafood.trycloudshell.com) *(ephemeral tunnel — may rotate)*

---

## Current Architecture

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│   TTS Audio  │───→│ LivePortrait │───→│   Wav2Lip    │───→│   Compose    │
│  (edge-tts)  │    │  (head move) │    │  (lip sync)  │    │  (slides)    │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
                                                                  ↑
                                                          Slides (Chromium)
```

**Pipeline stages:**
1. **Slide rendering** — Chromium headless renders HTML slides to 1920×1080 PNG
2. **TTS generation** — `edge-tts` (Microsoft Edge neural voice, no API key needed)
3. **Avatar animation** — LivePortrait drives head motion from a driving video
4. **Lip synchronization** — Wav2Lip syncs mouth to actual audio waveform
5. **Composition** — FFmpeg overlays avatar on slides + mixes audio
6. **Gallery** — Auto-generated `index.html` with per-video detail pages

---

## Quick Start

```bash
source venvs/lp-env/bin/activate

# Single slide
python scripts/pipeline.py \
  --topic "Neural Radiance Fields" \
  --text "NeRF reconstructs 3D scenes from 2D images..." \
  --output assets/output/demo.mp4

# Multi-slide presentation (JSON deck)
python scripts/pipeline.py \
  --presentation presentations/nerf_presentation.json \
  --output assets/output/nerf_presentation.mp4
```

---

## Documentation

| Page | Description |
|------|-------------|
| [**LOG →**](docs/LOG.md) | Full build log — what was implemented and when |
| [**AUDIO API →**](docs/AUDIO_API.md) | Voice Agent integration spec — what API we need |
| [**IMAGES →**](docs/IMAGES.md) | Avatar / Image Agent integration spec — what we need |
| [**SETUP.md**](SETUP.md) | Full environment reproduction guide |

---

## Current Limitations (Placeholder Phase)

| Component | Current | Needed |
|-----------|---------|--------|
| **Avatar** | Generic public-domain face | Prof. Hahne likeness from Image Agent |
| **Voice** | `edge-tts` offline voice | Real voice clone from Voice Agent API |
| **TTS provider** | Microsoft Edge (free) | Custom voice endpoint |

The pipeline is fully functional with placeholders. Swapping to real APIs is a **drop-in replacement** — no structural changes needed. See [AUDIO_API.md](docs/AUDIO_API.md) and [IMAGES.md](docs/IMAGES.md) for the exact contract.

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Deepfake engine | LivePortrait |
| Lip-sync | Wav2Lip (pretrained, GAN variant) |
| TTS | edge-tts (placeholder) |
| Slide renderer | Chromium headless (Hermes built-in) |
| Video composer | FFmpeg |
| GPU | NVIDIA RTX A6000 (48 GB) |
| Python | 3.10.14 (via `uv`) |
| Gallery | Auto-generated static HTML |

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
│   ├── pipeline.py        ← Main pipeline (4 steps + lip-sync)
│   ├── generate_index.py  ← Gallery + detail page generator
│   ├── start_server.sh    ← Local gallery server
│   └── start_tunnel.sh    ← Cloudflare tunnel
├── presentations/
│   └── nerf_presentation.json  ← Example 5-slide deck
├── assets/
│   ├── avatars/           ← Face images (placeholder)
│   ├── audio/             ← TTS outputs
│   ├── slides/            ← HTML sources + rendered PNGs
│   └── output/            ← Final MP4s + gallery index
├── LivePortrait/          ← Deepfake engine + weights
└── wav2lip/               ← Lip-sync engine + checkpoints
```

---

## Gallery Preview

The pipeline auto-generates:
- **`index.html`** — dark-mode gallery with video cards
- **`detail/{video}.html`** — per-video pages showing slide list, voice used, metadata, raw JSON

Generated on every pipeline run. Gallery server runs on port 8888.

---

*Prof. Dr. Uwe Hahne @ Hochschule Furtwangen | GenAI Educational Media Project*
