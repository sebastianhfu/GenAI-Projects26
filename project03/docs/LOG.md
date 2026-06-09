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

---

## Phase 7: Avatar Quality Iteration — Root-Cause Diagnosis (v4–v8)

**Problem identified:** LivePortrait copies **mouth motion directly from the driving video**, not from the TTS audio. This causes:
- v4–v6: Exaggerated mouth flapping, completely unsynced to spoken words
- v7: `--animation-region pose` fixed the mouth but eliminated all facial expression (too static)
- **Root cause:** The driving video (`d6.mp4`) contains its own mouth movements. LivePortrait transfers these 1:1.

**Solution for v8:**
1. Use `d0.mp4` (natural idle with subtle sway + blinks) as driving video
2. Apply Wav2Lip-SD-**NOGAN**.pt for sharper mouth quality (NOGAN variant avoids GAN artifacts)
3. Resize avatar to **350px** (previously 480px was too dominant)
4. Use CRF 20 for sharp encoding

**Result:** `videoretalking_presentation_v8.mp4` — significantly improved with natural idle motion + sharp lipsync. Still not perfect but usable.

---

## Phase 8: Hallo2 Diffusion Integration (v9)

**Goal:** Replace LivePortrait+Wav2Lip with a **single diffusion model** that natively handles audio-driven lip-sync + natural head motion.

**Why Hallo2:**
- Audio-conditioned diffusion — lips move based on TTS audio waveform, not a separate driving video
- Natural head sway + blinks generated natively by the model
- Higher visual quality than LivePortrait + Wav2Lip stacked
- One inference pass instead of two separate models

**Setup:**
1. Cloned `github.com/fudan-generative-vision/Hallo2.git`
2. Installed dedicated venv (`/opt/data/Hallo2/venv`) with torch 2.2.2+cu121, xformers, diffusers
3. Downloaded pretrained models (~40 files, ~2GB) from HuggingFace `fudan-generative-ai/hallo2`
4. Configured `hallo_full.yaml` with:
   - `source_image`: `prof_hahne_v4_512.jpg` (real photo)
   - `driving_audio`: concatenated 5-slide TTS (97.2s, 16kHz mono WAV)
   - `inference_steps`: 20 (reduced from 40 for speed — ~2× faster)
   - `512×512` output, 25fps

**Speed optimization:**
- Original 40 steps: ~2.5–3 hours estimated
- Reduced to 20 steps: ~50 minutes actual (per batch: 21s vs 42s)
- Quality tradeoff: slightly softer but acceptable — v-prediction scheduler handles low steps well

**ONNXRuntime CUDA mismatch (non-blocking):**
- Face analysis falls back to CPU: `libcublasLt.so.11` missing
- System has CUDA 12.1; ONNXRuntime built against 11.8
- Diffusion runs on GPU fine at 100% utilization

**Composition (`build_hallo2_presentation.py`):**
- Hallo2 output: `/tmp/hallo2_full_output/.../merge_video.mp4` (512×512, 97.2s)
- Loops video to total slide duration
- Scales to **350px** via lanczos
- Overlays on each slide at bottom-right (W-w-30, H-h-30)
- Burns HFU logo at top-right (W-160:30)
- CRF 20, slow preset

**Output:**
- `assets/output/hallo2_presentation.mp4` — 6.1MB, 1920×1080, 97.2s
- `assets/output/hallo2_presentation.json` — manifest with 5 slides
- Detail page: `detail/hallo2_presentation.html`

**Gallery update:**
- Added cache-busting query params (`?t=...`) to all video URLs
- Added `Cache-Control: no-cache` meta tags to index.html
- Filters: skips `_looped.mp4`, skips videos without JSON manifests

### Version Comparison

| Version | Engine | Lip-sync Source | Motion | Quality | Verdict |
|---------|--------|----------------|--------|---------|---------|
| v4–v6 | LivePortrait + Wav2Lip | Driving video (d6) | Extreme, unsynced | ❌ Poor | Mouth flapping |
| v7 | LivePortrait (`pose`) + Wav2Lip | Audio (via Wav2Lip) | Static, no eyes | ⚠️ Acceptable | Too lifeless |
| v8 | LivePortrait (`d0`) + Wav2Lip-NOGAN | Audio (via Wav2Lip) | Natural idle | ✅ Good | Best legacy |
| **v9** | **Hallo2 diffusion** | **Audio (native)** | **Natural + blink** | **✅ Best** | **Preferred** |

---

## Phase 9: Documentation Refresh (Current)

**Updates:**
- `README.md` — updated status, added Hallo2 architecture, version table, current state table
- `SETUP.md` — added Hallo2 installation section
- `LOG.md` — appended Phases 7–8 with root-cause analysis and speed optimization details
- `docs/projects/project03/index.md` — synced with README for MkDocs site

---

## Current State Summary

| Feature | Status |
|---------|--------|
| Single-slide videos | ✅ Working |
| Multi-slide presentations | ✅ Working |
| TTS (placeholder) | ✅ Working (edge-tts) |
| LivePortrait avatar | ✅ Working (legacy) |
| Wav2Lip lip-sync | ✅ Working (legacy) |
| **Hallo2 diffusion avatar** | **✅ Preferred** |
| Real avatar (Prof. Hahne) | ✅ Integrated (`prof_hahne_v4_512.jpg`) |
| Gallery generation | ✅ Working (cache-busting) |
| Detail pages | ✅ Working |
| GPU acceleration | ✅ Working |

### Generated Videos
| Video | Slides | Duration | Engine | Quality |
|-------|--------|----------|--------|---------|
| `hallo2_presentation.mp4` | 5 | 97.2s | Hallo2 (20 steps) | ✅ Best |
| `videoretalking_presentation_v8.mp4` | 5 | 97.2s | LivePortrait + Wav2Lip | ✅ Good |
| `hallo2_test.mp4` | 1 | 17.4s | Hallo2 (40 steps) | ✅ Test |

---

*Log maintained by Hermes Agent | Last updated: June 9, 2026*
