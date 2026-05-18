# Documentation — Project 3 (Educational Video Generation System)

## Project Description

This project plans a system for the automated creation of didactic explainer
videos in the style of a PowerPoint presentation with a presenter. The idea is
that a user enters a topic and the system produces a complete video in which an
avatar-based presenter explains slide contents.

The presenter avatar is planned to be modelled on **Prof. Dr. Uwe Hahne**, Dean
of Studies (Studiendekan) for Innovation Engineering (M.Sc.), Medieninformatik
(M.Sc.), and Sales & Service Engineering (MBA) at **Hochschule Furtwangen
University (HFU)**, Faculty I: Computer Science & Applications. His research
focuses on 3D computer vision, depth imaging, augmented and mixed reality,
human–computer interaction, and Neural Radiance Fields (NeRF) for industrial
applications. Consequently, the demo topics suggested below are drawn directly
from these subject areas.

> **Note:** This page describes the planning state only. No implementation, no
> training, and no generation has been performed.

---

## Planned System Architecture

The system is designed as a **distributed multi-agent pipeline** in which three
autonomous agents collaborate, coordinated by Hermes as the Presentation Agent.

### Multi-Agent Roles

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Image Agent** (external) | Avatar Material Provider | Generates and delivers reference face images for the presenter avatar. Images are provided once per character and cached locally for reuse. |
| **Voice Agent** (external) | Voice Synthesis Service | Clones voices on demand and synthesizes speech audio for specific text passages requested by the Presentation Agent. Exposes a REST API. |
| **Presentation Agent (Hermes)** | Orchestrator & Renderer | Generates slide content and narration scripts; requests audio from the Voice Agent; generates the deepfake talking-head video locally; composes the final presentation with slides, avatar video, and audio. |

### Data Flow

```
┌─────────────────┐     ┌──────────────────────┐
│  Image Agent    │────►│ Reference face image │
│  (external)     │     │ (one-time intake)    │
└─────────────────┘     └──────────┬───────────┘
                                     │
                                     ▼
                           ┌──────────────────┐
                           │  Local Cache     │  Presentation Agent stores
                           │  (avatars/*.jpg) │  validated avatar images
                           └──────────────────┘
                                    │
User ──► Presentation Agent        │
   "Create NeRF explainer"         │
         │                          │
         ├──► Generates slide outline & narration script
         │                          │
         ├──► POST /speak to Voice Agent
         │     {text: "...", voice_id: "..."}
         │                          │
         │◄── Receives audio blob (WAV/MP3) or download URL
         │                          │
         ├──► Generates deepfake talking-head
         │     Input: cached avatar image + audio
         │     Tool: Wav2Lip / LivePortrait / SadTalker (local)
         │     Output: synced avatar video clip (MP4)
         │                          │
         ├──► Renders slide visuals  │
         │     (Manim / Reveal.js / Pandoc + HTML)
         │                          │
         └─► FFmpeg composition      │
              Slides + avatar video + audio → final MP4
                        │
                        ▼
              ┌──────────────────┐
              │  Final MP4 File  │  Presentation output
              └──────────────────┘
```

### Currently Available

- Hermes Agent as the orchestration system (running)
- Basic concept idea and this planning documentation

### Not Yet Available / Future

- **Image Agent service:** Connection protocol defined (REST v1), awaiting endpoint URL from other team
- **Voice Agent service:** API contract defined (REST v1), awaiting endpoint URL from other team
- **Local deepfake pipeline:** Tool selected (LivePortrait primary, Wav2Lip fallback); needs installation
- **Reveal.js slide generator:** Method selected; needs template scaffolding
- **FFmpeg composition script:** Pipeline design complete; implementation pending

---

## Voice Service API Specification (Required)

The Voice Agent is an **external REST API service** responsible for
text-to-speech synthesis using its own built-in voices. The Presentation Agent
calls it on demand, once per slide narration passage. **No external voice
samples or cloning are required** — all voices are managed internally by the
Voice Agent.

### Base URL

```
V0 (proposed): https://<voice-agent-host>:<port>/api/v1
```

### Authentication

| Header | Type | Description |
|--------|------|-------------|
| `Authorization: Bearer <token>` | API Token | Long-lived JWT or simple API key. Alternatively, `X-Voice-API-Key` header may be used. |

### Endpoints

#### 1. `POST /api/v1/speak`

Synthesize speech from text using the Voice Agent's built-in voice.

**Request:**
- `Content-Type: application/json`
- **Body:**
```json
{
  "text": "Neural Radiance Fields reconstruct a 3D scene...",
  "voice_id": "default",
  "output_format": "wav",
  "output_bitrate": 128,
  "speed": 1.0,
  "language": "en"
}
```
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | String | **Yes** | Text to synthesise. Max length TBD (e.g., 500–5000 chars) |
| `voice_id` | String | No | Built-in voice preset, e.g. `"default"`, `"formal"`, `"friendly"`. Defaults to `"default"`. |
| `output_format` | String | No | `"wav"`, `"mp3"` (default: `"wav"`) |
| `output_bitrate` | Integer | No | Bitrate in kbps for lossy formats (default: `128`) |
| `speed` | Float | No | Playback speed factor (default: `1.0`) |
| `language` | String | No | ISO 639-1 override, e.g., `"en"`, `"de"` |

**Response (200 OK):**

Two variants depending on server capability (must be documented by provider):

**Variant A — Direct Audio Blob:**
- `Content-Type: audio/wav` (or `audio/mpeg` for MP3)
- Response body: raw audio bytes

**Variant B — Download URL (recommended when >10 MB):**
- `Content-Type: application/json`
- Response body:
```json
{
  "job_id": "job_9f8e2d1a",
  "status": "processing",
  "estimated_duration_sec": 15
}
```
Client then polls `GET /api/v1/jobs/{job_id}` until `status` becomes
`"completed"`, then downloads from `output_url`.

**Errors:**
- `400 Bad Request` — Text too long, invalid voice_id, unsupported format
- `401 Unauthorized`
- `404 Not Found` — voice_id does not exist
- `429 Too Many Requests` — Rate limit exceeded
- `500/503` — Server-side synthesis error / queue full

#### 2. `GET /api/v1/jobs/{job_id}` (Optional, required for Variant B)

Poll the status of an asynchronous speak job.

**Response (200 OK):**
```json
{
  "job_id": "job_9f8e2d1a",
  "status": "completed",
  "progress": 100,
  "output_url": "https://cdn.voice-agent.example/audio/job_9f8e2d1a.wav",
  "output_format": "wav",
  "duration_sec": 12.4,
  "expires_at": "2026-05-18T15:00:00Z"
}
```

| Status | Meaning |
|--------|---------|
| `"pending"` | Queued, not yet started |
| `"processing"` | Synthesis in progress |
| `"completed"` | Ready for download at `output_url` |
| `"failed"` | Error; check `error_message` field |

#### 3. `GET /api/v1/voices` (Optional)

List all built-in voices available on the Voice Agent.

**Response (200 OK):**
```json
{
  "voices": [
    {
      "voice_id": "default",
      "name": "Default",
      "description": "General purpose",
      "language": "en",
      "gender": "male"
    },
    {
      "voice_id": "formal",
      "name": "Formal",
      "description": "Professional presenter style",
      "language": "en",
      "gender": "male"
    }
  ]
}
```

### Rate Limits & Quotas (To be confirmed by Voice Agent provider)

| Resource | Proposed Limit |
|----------|---------------|
| `/speak` text characters | e.g., 100,000 per day |
| Max text length per `/speak` | e.g., 5,000 characters or 10 minutes audio |
| Download URL expiry | e.g., 24 hours |

### Error Handling Responsibilities

| Layer | Behaviour |
|-------|-----------|
| **Presentation Agent** | Retry `GET /jobs/{}` up to N times with exponential backoff; fallback to a default TTS voice if Voice Agent fails; log and skip slide if all fallbacks exhausted. |
| **Voice Agent** | Return clear HTTP status codes + JSON `error_message`; never hang indefinitely on generation requests. |

---

## Image Agent Interface Specification (Required)

The Image Agent is an **external service** responsible for generating or
providing reference face images for the presenter avatar. The Presentation Agent
receives images via a one-time intake and caches them locally for all subsequent
deepfake generations.

### Base URL

```
V0 (proposed): https://<image-agent-host>:<port>/api/v1
```

### Authentication

| Header | Type | Description |
|--------|------|-------------|
| `Authorization: Bearer <token>` | API Token | Long-lived JWT or simple API key. |

### Endpoints

#### 1. `POST /api/v1/avatars`

Generate or upload a reference face image for a new presenter character.

**Request (if generating):**
- `Content-Type: application/json`
- **Body:**
```json
{
  "character_name": "Prof. Hahne",
  "prompt": "Professional head-and-shoulders portrait of a middle-aged male professor, ...",
  "style": "photorealistic",
  "negative_prompt": "blurry, low quality, multiple faces, ...",
  "return_format": "url"
}
```

**Request (if uploading seed images for generation):**
- `Content-Type: multipart/form-data`
- **Body Fields:**
  - `seed_images[]` (Files, required) — Reference photos of the person
  - `character_name` (String, required)

**Response (201 Created — URL variant):**
```json
{
  "avatar_id": "avt_9b2c4d1e",
  "character_name": "Prof. Hahne",
  "image_url": "https://cdn.image-agent.example/avatars/avt_9b2c4d1e.jpg",
  "dimensions": [1024, 1024],
  "format": "jpeg",
  "expires_at": "2026-06-18T10:00:00Z"
}
```

**Response (201 Created — Base64 variant, not recommended for large files):**
```json
{
  "avatar_id": "avt_9b2c4d1e",
  "character_name": "Prof. Hahne",
  "image_base64": "/9j/4AAQSkZJRgABAQAAAQ...",
  "dimensions": [1024, 1024],
  "format": "jpeg"
}
```

**Errors:**
- `400 Bad Request` — Invalid prompt, unsupported format
- `401 Unauthorized`
- `413 Payload Too Large` — Upload size exceeded
- `422 Unprocessable Entity` — Generation failed, no face detected

#### 2. `GET /api/v1/avatars/{avatar_id}`

Download a previously generated avatar image.

**Response:**
- `Content-Type: image/jpeg` (or `image/png`)
- Body: raw image bytes (or 307 redirect to `image_url`)

#### 3. `GET /api/v1/avatars`

List all available avatars.

**Response (200 OK):**
```json
{
  "avatars": [
    {
      "avatar_id": "avt_9b2c4d1e",
      "character_name": "Prof. Hahne",
      "image_url": "https://cdn.image-agent.example/avatars/avt_9b2c4d1e.jpg",
      "dimensions": [1024, 1024],
      "created_at": "2026-05-18T10:00:00Z"
    }
  ]
}
```

#### 4. `DELETE /api/v1/avatars/{avatar_id}`

Remove an avatar. Returns `204 No Content`.

### Intake Workflow (Presentation Agent Side)

Once per project / per character:

```python
# 1. Request avatar from Image Agent
response = requests.post("https://image-agent/api/v1/avatars", json=payload)
avatar_url = response.json()["image_url"]

# 2. Download and validate locally
img = download(avatar_url)
assert img.width >= 512 and img.height >= 512
assert detect_face(img)  # at least one face visible

# 3. Cache locally
save(img, f"avatars/{avatar_id}.jpg")

# 4. Reuse for every slide's deepfake generation
```

### Local Cache Requirements

| Requirement | Spec |
|-------------|------|
| **Cache path** | `avatars/<avatar_id>.<ext>` |
| **Formats** | JPEG or PNG |
| **Min resolution** | 512×512 (recommended: 1024×1024) |
| **Max resolution** | 2048×2048 (to limit VRAM) |
| **Validation** | Face detected via OpenCV / MediaPipe dlib |
| **Cleanup** | Expire and re-request after 30 days or on demand |

---

## Open Technical Questions

The following points must be clarified before implementation can begin.

### Voice Agent

1. Which API does the voice server expose? *(Answered — assumed REST with `/clone`, `/speak`, `/jobs`)*
2. Which authentication is expected? *(Answered — `Bearer` token or `X-Voice-API-Key`)*
3. Which input format does the server need? Plain text; SSML optional? *(Open)*
4. Which output formats does the server deliver? *(Proposed: WAV or MP3, 24 kHz)*
5. Is there a length limit per request? *(Open — propose 5,000 chars / 10 min audio)*
6. Is batch processing possible, or only individual sentences? *(Open)*

### Image Agent

7. How are images delivered? *(Proposed: URL download + local cache)*
8. What resolution/format guarantee? *(Proposed: min 512×512, JPEG/PNG, frontal face)*
9. How long do images remain available on the Image Agent? *(Proposed: 30-day URL expiry, local cache canonical)*
10. Can multiple angles/expressions be requested for better deepfake quality? *(Open)*
11. Can the same avatar image be reused indefinitely, or per-project refresh required? *(Proposed: indefinite reuse, per-project refresh at agent discretion)*
12. Are there licence restrictions on generated images? *(Open — consent for Prof. Hahne required)*

### Presentation Agent (Local Pipeline)

13. **Deepfake tool selection** *(Answered — LivePortrait primary; Wav2Lip fallback)*
    - LivePortrait: best speed/quality, CUDA required, ~4 GB VRAM, 512–1024 px input
    - Wav2Lip: CPU-compatible fallback, slightly lower fidelity, slower
    - SadTalker: highest quality, very slow, reserved for final renders if needed
14. **Slide rendering** *(Answered — Reveal.js HTML slides + Chrome headless capture)*
15. **Synchronisation** *(Open — word-level timestamps from Voice Agent needed?)*
16. **Final composition layout** *(Answered — see Pipeline Design below)*

### Data Flow & Infrastructure

17. How are generated assets transferred? *(Proposed: URL + local download, no shared storage dependency)*
18. Where is the final video rendered? *(Answered — locally on Hermes machine via FFmpeg)*
19. Which latency is acceptable? *(Open — target: <5 min for a 2-slide demo)*
20. Error handling strategy? *(Proposed: retry 3× with backoff, fallback to default voice, skip-slide fallback)*
21. Storage/bandwidth constraints? *(Open)*

### Legal and Ethical Questions

22. Which consent documentation exists for the avatar used (Prof. Dr. Uwe Hahne)? *(Open)*
23. Which licence conditions apply to the generated videos? *(Open)*
24. Which notices must be included? *(Proposed: watermark text — "AI-generated avatar & voice")*
25. Are there restrictions on public publication? *(Open)*

### Tooling Selection (Answered)

| Decision | Chosen Tool | Rationale |
|----------|-------------|-----------|
| Deepfake engine | **LivePortrait** | Real-time inference, single-image input, high-quality lip-sync and head motion, 4 GB VRAM minimum, supports arbitrary driving audio |
| Deepfake fallback | **Wav2Lip** | CPU-compatible, well-tested, lower fidelity but always available |
| Slide renderer | **Reveal.js** + Chrome Headless | HTML-based, easy to generate dynamically, can be captured to video frame-by-frame or stitched as image sequence |
| Slide-to-video | **Chrome DevTools Protocol** or **Playwright** | Render Reveal.js to images/MP4 at target resolution |
| Composition | **FFmpeg** | Overlay avatar onto slides, mix audio, add intro/outro fades |
| Avatar preprocessing | **OpenCV / dlib / MediaPipe** | Face detection, alignment, cropping to LivePortrait input specs |

---

## Pipeline Design — Full Architecture

This section details how the Presentation Agent executes the complete end-to-end
flow from a topic string to a final MP4 video.

### Step-by-Step Flow

```
┌──────────────┐
│  User Input  │  "Explain NeRF in 3 slides"
└──────┬───────┘
       ▼
┌────────────────────────────┐
│  Step 1: Script Generation │  Hermes writes outline + narration text
│  (Presentation Agent)      │  per slide (~30–90 sec each)
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│  Step 2: Slide Rendering │  Generate Reveal.js HTML slides
│  (Presentation Agent)      │  Capture each slide to static image
│                            │  (Playwright / Chrome headless)
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│  Step 3: Audio Generation  │  POST /api/v1/speak per slide
│  (Voice Agent API)         │  Returns WAV/MP3 audio file
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│  Step 4: Deepfake Avatar   │  LivePortrait generates talking-head
│  (Local GPU, LivePortrait) │  from cached avatar image + audio
│                            │  Output: MP4 (avatar with audio lipsync)
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│  Step 5: Composition       │  FFmpeg overlays avatar onto slide image,
│  (Local, FFmpeg)           │  syncs on each slide's audio duration,
│                            │  adds intro/outro fade, watermark
└────────────┬───────────────┘
             ▼
┌────────────────────────────┐
│  Final MP4                 │  Continuous video: slides + talking avatar
└────────────────────────────┘
```

### Tool Selections

#### 1. Deepfake — LivePortrait (Primary)

LivePortrait takes a **single static portrait image** and a **driving audio**
(and optionally a driving video for expressions) and produces a realistic
animated talking-head video with natural head motion, eye blinks, and lip
synchronisation. It is the current best open-source choice for one-image
animation because:

* **Speed** — Real-time inference on modern GPUs; a 30-second clip in <30 s.
* **Quality** — High-fidelity facial animation, no uncanny-stiff head.
* **Input flexibility** — Single image is sufficient (no video or mesh needed).
* **Audio driven** — Can accept raw audio via a helper pipeline (audio →
  expression coefficients → animation).

**Requirements:**
* GPU with ≥4 GB VRAM (ideally ≥8 GB for 1024×1024 input)
* PyTorch ≥2.0, CUDA toolkit matching PyTorch version
* Input image: 512×512 or 1024×1024, frontal face clearly visible
* Linux recommended (available for this system ✓)

**Alternatives evaluated:**

| Tool | Speed | Quality | VRAM | Pros | Cons |
|------|-------|---------|------|------|------|
| *(Primary)* | | | | | |
| **LivePortrait** | Real-time | Excellent | 4–8 GB | Best single-image animation | Needs expression model for pure audio |
| *Fallbacks* | | | | | |
| **Wav2Lip** | Slow-ish | Good | 2–4 GB | Mature, works CPU-only | Head is static, less natural |
| **SadTalker** | Very slow | Excellent | 8+ GB | Highest lip fidelity | Inference ~1 min per 10 s audio |
| **Sieve / EMO** | Cloud | Best | N/A | Unbeatable realism | Proprietary / costly |

> **Decision:** LivePortrait as the primary engine. Wav2Lip as CPU fallback if
> CUDA is unavailable. SadTalker reserved for final high-polish renders on
> request.

#### 2. Slide Rendering — Reveal.js + Chrome Headless

**Why Reveal.js?**
* Native HTML—easy to generate from templates in Python.
* Has a **print-to-PDF** mode and can be screenshot via `Playwright` or Puppeteer.
* Supports automatic transition timing.
* Can render code blocks, MathJax, images, and animations.

**How to turn slides into video frames:**
```bash
# Option A: Capture each slide as an image, then stitch
cd slides/
npx playwright screenshot index.html slide_01.png --viewport-size=1920,1080
# ... repeat per slide → feed to FFmpeg as image sequence

# Option B: Single Reveal.js export script using Chrome DevTools Protocol
python render_slides.py --output-dir frames/ --resolution 1920x1080
```

**Recommended slide layout** for video (to leave room for avatar):
```css
.reveal .slides section {
  padding-right: 400px;   /* Leave right margin for avatar overlay */
}
```
Or, for split-screen:
```
┌─────────────────┬────────┐
│                 │        │
│   Slide content │ Avatar │
│   (left 70%)    │(right  │
│                 │  30%)  │
└─────────────────┴────────┘
```

#### 3. Composition Layout — FFmpeg Overlay

**Proposed layout** (final video 1920×1080):

| Layer | Position | Size |
|-------|----------|------|
| Slide background | Full canvas (z=0) | 1920×1080 |
| Slide content | Left 70% (z=1) | 1344×1080, padded |
| Avatar (LivePortrait output) | Bottom-right corner (z=2) | 576×768 (upscaled from 512×512) |
| Audio track | Mixed in (z=audio) | 48 kHz stereo |
| Watermark | Bottom-left (z=3) | "AI-generated avatar & voice" |

**FFmpeg composition for one slide:**
```bash
ffmpeg -y \
  -loop 1 -i "slide_01.png" \
  -i "avatar_01.mp4" \
  -i "slide_01.wav" \
  -filter_complex "
    [0:v]scale=1920:1080[bg];
    [1:v]scale=576:-1,format=yuva420p,setpts=PTS-STARTPTS[ava];
    [bg][ava]overlay=W-w-20:H-h-20[comp];
    [comp]drawtext=text='AI-generated avatar & voice':
      fontcolor=white@0.5:fontsize=18:x=20:y=H-th-20[final]
  " \
  -map "[final]" -map 2:a \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -b:a 192k \
  -t "$DURATION" "slide_01_composed.mp4"
```

**Concatenation** for multi-slide video:
```bash
# Create concat list
echo "file 'slide_01_composed.mp4'" > concat.txt
echo "file 'slide_02_composed.mp4'" >> concat.txt

# Concat with cross-fade
ffmpeg -f concat -safe 0 -i concat.txt \
  -c copy "final_presentation.mp4"
```

### File Structure

```
project03/
├── assets/
│   ├── avatars/
│   │   └── avt_9b2c4d1e.jpg        # Cached from Image Agent (one-time intake)
│   ├── audio/
│   │   ├── slide_01.wav            # From Voice Agent per slide
│   │   └── slide_02.wav
│   ├── slides/
│   │   ├── index.html              # Generated Reveal.js deck
│   │   ├── slide_01.png            # Captured slide images
│   │   └── slide_02.png
│   └── deepfakes/
│       ├── avatar_01.mp4           # LivePortrait output per slide
│       └── avatar_02.mp4
├── output/
│   ├── slide_01_composed.mp4
│   ├── slide_02_composed.mp4
│   └── final_presentation.mp4      # Final output
└── scripts/
    ├── generate_slides.py          # Step 1: Reveal.js generation
    ├── call_voice_api.py           # Step 2: Voice Agent client
    ├── generate_deepfake.py        # Step 3: LivePortrait wrapper
    └── compose_video.py            # Step 4: FFmpeg composition
```

### Timing Strategy

Each slide needs its own audio duration. To sync the slide-to-avatar video:

1. Generate audio → get exact duration `T` via `ffprobe` or `pydub`.
2. Render slide as a still image that loops for `T` seconds.
3. Run LivePortrait with audio length = `T` → avatar video also = `T`.
4. Overlay both and output a clip of exactly `T` seconds.
5. Concatenate all clips in order.

### GPU/VRAM Budget Estimate

| Operation | VRAM (est.) | Time (30 s audio) |
|-----------|------------|-------------------|
| LivePortrait inference (512×512) | 4–6 GB | 5–15 s |
| LivePortrait inference (1024×1024) | 6–8 GB | 10–25 s |
| FFmpeg composition (CPU) | 0 GB | 1–2 s per clip |
| Slide capture (Playwright) | 0 GB | 1 s per slide |
| **Total per slide** | **4–8 GB** | **<1 min typical** |

---

## Suggested Presentation Topics

For later prototyping, topics should be short enough for a demo video (approx.
1–3 minutes) but technically substantial enough to demonstrate the usefulness
of the system. The topics below are aligned with the research and teaching
areas of **Prof. Dr. Uwe Hahne** at Hochschule Furtwangen University —
primarily **3D computer vision, depth imaging, augmented/mixed reality,
human–computer interaction, Neural Radiance Fields (NeRF), and media
informatics**.

### Topic Categories

- Neural Radiance Fields and 3D Reconstruction
- Depth Imaging and 3D Computer Vision
- Augmented, Mixed, and Virtual Reality
- Human–Computer Interaction and Multi-Touch
- Computer Graphics and Visualisation
- Media Informatics and Industrial Applications

### Concrete Topic Suggestions

| No. | Topic | Why It Fits Prof. Hahne's Research |
|-----|-------|-----------------------------------|
| 1 | **What are Neural Radiance Fields (NeRF)?** | Direct match — 2024 paper on NeRFs for the Industrial Metaverse |
| 2 | **How does NeRF reconstruct a 3D scene from photos?** | Core NeRF technology |
| 3 | **What is the difference between NeRF and traditional 3D scanning?** | NeRF vs. conventional depth imaging |
| 4 | **How does a Time-of-Flight (ToF) camera measure depth?** | Direct match — PhD thesis and multiple papers on depth imaging |
| 5 | **How does stereo vision estimate depth?** | 2008/2009 papers on combining ToF and stereo |
| 6 | **What is depth image fusion?** | 2011 paper: "Exposure Fusion for Time-of-Flight Imaging" |
| 7 | **How does the HoloLens display augmented reality?** | Direct match — 2017 paper on HoloLens and 3D sensors |
| 8 | **What is the difference between AR, MR, and VR?** | AR/MR research lineage |
| 9 | **How do multi-touch screens track fingers?** | Direct match — 2008 SIGGRAPH paper on FTIR touch sensing |
| 10 | **How does perspective projection affect 3D interaction?** | Direct match — 2012 paper on perspective projection in multi-touch 3D |
| 11 | **What is sketch-based interaction?** | Direct match — 2009 paper on multi-touch sketch-based interaction |
| 12 | **How does focus-plus-context interaction work?** | Direct match — 2009 paper on focus+context sketch interaction |
| 13 | **What is the rendering pipeline in computer graphics?** | Graphics foundations |
| 14 | **How does exposure bracketing create HDR images?** | Links to exposure fusion research |
| 15 | **What is an industrial metaverse?** | Direct match — 2023/2024 NeRF-for-metaverse papers |
| 16 | **How can 3D scanning digitise a factory floor?** | Industrial 3D vision application |
| 17 | **What is a point cloud and how is it used?** | 3D vision fundamentals |
| 18 | **How does photogrammetry create 3D models?** | Related to NeRF and depth imaging |
| 19 | **What is inside-out tracking for VR headsets?** | Depth sensors + tracking |
| 20 | **How does a depth sensor work under different lighting?** | Depth imaging robustness |
| 21 | **What is simultaneous localisation and mapping (SLAM)?** | 3D vision + robotics overlap |
| 22 | **How can AR overlays guide industrial maintenance?** | HoloLens / industrial AR application |
| 23 | **What is tangible interaction?** | HCI extension from touch research |
| 24 | **How does a computer recognise hand gestures?** | Vision + HCI overlap |
| 25 | **What is spatial computing?** | Modern framing of AR/MR/VR research |

> **Recommended Prototype Topics:** No. 1, 4, 7, 9, or 15 — these are
> concise, visually supportable, and directly grounded in Prof. Hahne's
> published research.

---

## Proposed Development Phases

### Phase 1 — Concept and Requirements (Mostly Complete)

**Goal:** Define clear framework conditions before technical work begins.

- [x] Define target video format: **MP4, 1920×1080, 30 fps, H.264, AAC audio**
- [x] Identify external services: Image Agent (image provider), Voice Agent (TTS)
- [x] Define input/output formats: topic string in → MP4 video out
- [ ] Select one prototype topic from the list above
- [ ] Check legal consent for avatar and voice usage

**Result:** Requirements document, selected topic, confirmed service availability.

### Phase 2 — Interface Planning (Complete)

**Goal:** Define API contracts and data flows between Hermes, the voice server,
and the avatar server.

- [x] Create API specification for voice server (request/response schema, auth, error codes) — documented in this file
- [x] Create API specification for image server — documented in this file
- [x] Decide file transfer method: **URL download + local cache**
- [x] Document expected response formats (Audio: **WAV 24 kHz**; Video: **MP4 H.264**)
- [x] Define job-status polling schema: exponential backoff, max 10 retries

**Result:** API documentation preserved in this doc. OpenAPI spec optional future work.

### Phase 3 — Tool Setup and Pipeline Scaffold

**Goal:** Install and configure the local deepfake and slide-rendering stack.

- [ ] Clone and install **LivePortrait** with PyTorch + CUDA
- [ ] Test LivePortrait with a sample image + audio → verify output
- [ ] Build **Reveal.js HTML slide generator** (Python template → HTML)
- [ ] Build **slide-to-image capture** (Playwright or Chrome headless)
- [ ] Scaffolding for `generate_slides.py`, `generate_deepfake.py`, `compose_video.py`

**Result:** Each script works in isolation; can be run manually end-to-end.

### Phase 4 — Integration and End-to-End Test

**Goal:** Wire all pieces together into a single orchestration flow.

- [ ] Implement mock Voice Agent (for offline testing) or connect real endpoint
- [ ] Implement mock Image Agent (for offline testing) or connect real endpoint
- [ ] Implement voice-service client (`call_voice_api.py`)
- [ ] Implement avatar intake script (`intake_avatar.py`)
- [ ] Implement full orchestrator: topic → slides → audio → deepfake → video
- [ ] Test with real generated assets and evaluate quality/speed

**Result:** Working prototype that produces a demo video for the selected topic.

---

## Lessons Learned

> *To be added once Phases 1–3 are completed and initial insights are
> available.*

## Results

!!! note "Work in Progress"
    Results will be documented here once the project is completed.
    At present only the planning documentation is available.
