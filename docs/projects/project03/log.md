# Project 3 — Build Log

Chronological record of everything implemented to reach the current pipeline state.

---

## Phase 1: Foundation (Initial Setup)

### Environment
- **Python 3.10.14** installed side-by-side via `uv` (system is 3.13.5, LivePortrait requires ~3.10)
- **cuDNN compatibility fix:** Extracted cuDNN 8.9 side-by-side with cuDNN 9.1
  - PyTorch uses cuDNN 9.x
  - ONNX Runtime 1.18 requires cuDNN 8.x
  - `pipeline.py` auto-sets `LD_LIBRARY_PATH` to both paths before inference
- **GPU verified:** 1184 MiB usage during inference, zero CPU-fallback warnings

### Tools Installed
| Tool | Version | Purpose |
|------|---------|---------|
| PyTorch | 2.7.1+cu118 | LivePortrait inference |
| ONNX Runtime | 1.18.0 | Face detection backend |
| edge-tts | latest | Placeholder TTS (no API key) |
| FFmpeg | 7.1.3 | Video composition |
| Chromium | 1217 (headless shell) | Slide rendering |

### Repositories Cloned
- `LivePortrait/` — Deepfake engine + pretrained weights from HuggingFace
- `wav2lip/` — Lip-sync engine + 2 checkpoints (GAN + no-GAN)

---

## Phase 2: Basic Pipeline (Single Slide)

**Goal:** Generate a single educational video: slide + TTS + avatar overlay

### Components Built
1. **`pipeline.py`** — 4-step CLI pipeline:
   - `--topic`, `--text`, `--output` args
   - Slide rendering via Chromium headless (1920×1080 PNG)
   - TTS via `edge-tts` (Microsoft Edge neural voice)
   - Avatar animation via LivePortrait
   - FFmpeg composition: slide background + avatar overlay + audio

2. **Slide HTML template** — Dark-themed, HFU branded, responsive typography

3. **`generate_index.py`** — Auto-generates `index.html` gallery

### First Output
- `assets/output/final_demo.mp4`
- `assets/output/pipeline_test.mp4`

---

## Phase 3: Multi-Slide Presentations

**Goal:** Support JSON slide decks for longer lectures

### Changes
1. **`--presentation` flag** added to `pipeline.py`
   - Accepts JSON file with `slides[]` array
   - Each slide gets independent TTS + rendered PNG
   - FFmpeg concatenates segments with per-slide timing

2. **Example presentation created:**
   - `presentations/nerf_presentation.json`
   - 5 slides about Neural Radiance Fields
   - Topics: What is NeRF, How it works, Volume rendering, Positional encoding, AR/MR applications

3. **Test result:** 74.8s final video, all 5 slides composited correctly

### Output
- `assets/output/nerf_presentation.mp4`
- `assets/output/nerf_presentation.json` (manifest)

---

## Phase 4: Gallery Enhancement (Detail Pages)

**Goal:** Per-video detail view with metadata, slide list, raw JSON

### Changes
1. **`generate_index.py` extended:**
   - Creates `detail/{video}.html` for every video with a manifest
   - Shows: full video player, slide-by-slide breakdown, voice used, raw metadata JSON
   - Download links + back navigation

2. **Manifest system added:**
   - Every generated video gets a `.json` manifest
   - Contains: topic, subtitle, voice, slide list, timestamps, duration

3. **Gallery filtering:**
   - Skip `*_looped.mp4` intermediates
   - Skip videos without `.json` manifests (prevents broken placeholders)

### Output
- `assets/output/index.html` (gallery)
- `assets/output/detail/nerf_presentation.html`

---

## Phase 5: Wav2Lip Lip-Sync Integration

**Goal:** Sync avatar mouth movements to actual TTS audio (not just pre-canned driving motion)

### Wav2Lip Setup
1. **Repository cloned:** `github.com/Rudrabha/Wav2Lip`
2. **Checkpoints downloaded:**
   - `Wav2Lip-SD-GAN.pt` (146 MB)
   - `Wav2Lip-SD-NOGAN.pt` (146 MB)
3. **Compatibility patches applied:**
   - `audio.py`: `librosa.filters.mel()` kwargs fix for librosa 0.11
   - `audio.py`: `librosa.load()` instead of deprecated `librosa.core.load()`
   - `audio.py`: `soundfile.write()` instead of removed `librosa.output.write_wav()`
   - `inference.py`: `torch.load(weights_only=False)` for PyTorch 2.7
   - `inference.py`: TorchScript archive fallback handling

### Pipeline Changes
1. **New stage added:** `lip_sync_avatar()`
   - Takes LivePortrait-animated video + audio file
   - Runs Wav2Lip inference
   - Outputs lip-synced avatar video

2. **Audio concatenation helper:** `concat_audios()`
   - Merges multiple slide MP3s into one WAV for Wav2Lip (multi-slide presentations)

3. **Pipeline flow updated:**
   ```
   Before: TTS → LivePortrait → Compose
   After:  TTS → LivePortrait → Wav2Lip → Compose
   ```

4. **Manifest updated:**
   - Added `"lip_sync": true`
   - Added `"lip_sync_engine": "Wav2Lip"`

### Test Results
| Test | Duration | Result |
|------|----------|--------|
| Wav2Lip standalone | 8.6s | ✅ Mouth synced to demo narration |
| Full pipeline (single slide) | 9.4s | ✅ End-to-end with lip-sync |

### Output
- `assets/output/lipsync_test.mp4`
- `assets/output/lipsync_test.json`

---

## Phase 6: Documentation Reorganization (Current)

**Goal:** Clean GitHub page with subpages for different audiences

### Structure Created
```
project03/
├── README.md           ← Landing page (status + quick start + links)
├── SETUP.md            ← Full reproduction guide
└── docs/
    ├── LOG.md          ← This file — build history
    ├── AUDIO_API.md    ← Voice Agent API contract (what we need)
    └── IMAGES.md       ← Image/avatar API contract (what we need)
```

### README.md rewritten as:
- Small status overview
- Architecture diagram
- Quick start commands
- Links to subpages
- Current limitations table
- Tech stack summary

---

## Current State Summary

| Feature | Status |
|---------|--------|
| Single-slide videos | ✅ Working |
| Multi-slide presentations | ✅ Working |
| TTS (placeholder) | ✅ Working (edge-tts) |
| Avatar animation | ✅ Working (LivePortrait) |
| **Lip-sync** | ✅ **Working (Wav2Lip)** |
| Gallery generation | ✅ Working |
| Detail pages | ✅ Working |
| GPU acceleration | ✅ Working (cuDNN 8/9 fix) |
| Real avatar (Prof. Hahne) | ⏳ Awaiting Image Agent |
| Real voice clone | ⏳ Awaiting Voice Agent API |

### Generated Videos
| Video | Slides | Duration | Lip-sync |
|-------|--------|----------|----------|
| `nerf_presentation.mp4` | 5 | 74.8s | ✅ |
| `lipsync_test.mp4` | 1 | 9.4s | ✅ |

---

## Known Issues / TODO

1. **Cloudflare tunnel URL is ephemeral** — rotates on restart. For stable preview, need custom domain or VPS port exposure.
2. **Gallery cache** — Browser may show stale entries; `Ctrl+Shift+R` hard refresh needed.
3. **Wav2Lip resize_factor** — Currently set to 1 (full resolution). May need tuning for 4K output.
4. **Audio-driven LivePortrait** — Alternative to Wav2Lip (better quality but slower). Deferred until needed.

---

*Log maintained by Hermes Agent | Last updated: June 4, 2026*
