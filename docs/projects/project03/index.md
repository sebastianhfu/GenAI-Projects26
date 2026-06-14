# Project 3 — GenAI Educational Media Pipeline

> **Status:** 🟢 Operational — Real avatar (Prof. Hahne) integrated. Hallo2 diffusion pipeline producing production-quality output.
> **Institution:** Hochschule Furtwangen (HFU), Faculty I: Computer Science & Applications
> **Project Lead:** Prof. Dr. Uwe Hahne

---

## Personal notes
### Setup
- Docker was used to host the hermes agent
- As the agent needs GPU acceleration, specific packages for docker nvidia GPU suport had to be installed
- Discord setup as a communication channel was somewhat annoying to deal with using this setup, especially to trust a given account

### Findings
- To modify the agent on the VM, the docker container has to be accessed
- I did not find it that intuitive to modify settings via docker cli + hermes cli
- The GitHub classic token to push and open PRs had to be entered over and over again, as it did not store it, probably due to security concerns
- Simple tasks can starve and manual intervention has to be done to try again
- Overall amount of given tokens using the ollama cloud plan was sufficient for the entire experiment
- Majority of the project instructions were done using the discord channel

### Project
- The entire project was executed by the agent
- Slight adjustments had to be made
- The agent managed to download models, setup the pipeline, a http tunnel and coding scripts on its own
- A few hallucinations happened during interacting with the agent, for example the required inference time on the given hardware

Overall i was quite impressed by the capabilities of open source agents as it still managed to setup the entire project on its own.

# VM Setup

## Storage Configuration

Create and mount the additional storage disk:

```bash
sudo fdisk /dev/sdb
sudo mkfs.ext4 /dev/sdb1

sudo mkdir -p /mnt/storage
sudo mount /dev/sdb1 /mnt/storage
sudo chown -R lecture:lecture /mnt/storage
```

Persist mount configuration:

```bash
sudo blkid /dev/sdb1
sudo nano /etc/fstab
sudo mount -a
```

Example entry:

```text
UUID=<UUID> /mnt/storage ext4 defaults,nofail 0 2
```

## SSH Configuration

Enable OpenSSH and configure key-based authentication:

```bash
sudo mkdir -p /run/sshd
sudo chmod 755 /run/sshd

sudo systemctl start ssh
sudo systemctl enable ssh
```

Generate an SSH key on the local machine:

```bash
ssh-keygen -t ed25519
cat ~/.ssh/id_ed25519.pub
```

Add the public key to the VM:

```bash
nano ~/.ssh/authorized_keys

chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

## Docker Installation

Install Docker and required dependencies:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git wget htop tmux unzip build-essential
```

Add the Docker repository and install Docker:

```bash
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Enable Docker usage without sudo:

```bash
sudo usermod -aG docker $USER
newgrp docker
```

Verify installation:

```bash
docker run hello-world
```

## NVIDIA Container Toolkit

Install and configure GPU support:

```bash
sudo apt install -y nvidia-container-toolkit

sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

Verify GPU passthrough:

```bash
docker run --rm --gpus all \
  nvidia/cuda:12.4.1-runtime-ubuntu22.04 \
  nvidia-smi
```

## Docker Data Migration

Create a dedicated storage location:

```bash
sudo mkdir -p /mnt/storage/docker
```

Configure Docker:

```bash
sudo nano /etc/docker/daemon.json
```

```json
{
    "data-root": "/mnt/storage/docker",
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}
```

Restart Docker:

```bash
sudo systemctl restart docker
```

Verify configuration:

```bash
docker info | grep "Docker Root Dir"
```

## Hermes Setup

Create persistent storage:

```bash
mkdir -p /mnt/storage/hermes
```

Run initial setup:

```bash
docker run -it --rm \
  --gpus all \
  -v /mnt/storage/hermes:/opt/data \
  nousresearch/hermes-agent setup
```

Configure environment variables:

```bash
nano /mnt/storage/hermes/.env
```

Example:

```text
OLLAMA_API_KEY=...
DISCORD_ALLOWED_USERS=252538619787476993
```

## Hermes Gateway Deployment

Configure the gateway:

```bash
docker run -it --rm \
  --gpus all \
  -v /mnt/storage/hermes:/opt/data \
  nousresearch/hermes-agent setup gateway
```

Start the persistent container:

```bash
docker run -d \
  --name hermes \
  --restart unless-stopped \
  --gpus all \
  -v /mnt/storage/hermes:/opt/data \
  -p 8642:8642 \
  nousresearch/hermes-agent gateway run
```

Verify operation:

```bash
docker logs hermes
docker ps
```

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
| [**LOG →**](log.md) | Full build log — what was implemented and when |
| [**AUDIO API →**](audio_api.md) | Voice Agent integration spec |
| [**IMAGES →**](images.md) | Avatar / Image Agent integration spec |

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
├── README.md              ← Landing page (project03/)
├── SETUP.md               ← Full reproduction guide
├── docs/                  ← MkDocs pages for the website
│   └── project03/
│       ├── index.md       ← This page (overview + status)
│       ├── log.md         ← Build history
│       ├── audio_api.md   ← Voice API contract
│       └── images.md      ← Image/avatar API contract
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
