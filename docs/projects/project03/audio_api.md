# Audio / Voice Agent API Specification

> **Purpose:** Define the API contract needed from the Voice Agent team so that `pipeline.py` can swap out `edge-tts` for a real voice clone of Prof. Hahne.
> **Current placeholder:** `edge-tts` (Microsoft Edge neural voice, offline, no API key)

---

## What We Need

A **REST API endpoint** that accepts text + voice parameters and returns:
- Synthesized audio (MP3/WAV)
- Optional: word-level timestamps for advanced lip-sync

---

## Required Endpoint

### `POST /speak` (or `/tts` / `/synthesize`)

**Request:**
```json
{
  "text": "Neural Radiance Fields enable photorealistic 3D scene reconstruction from sparse 2D images.",
  "voice_id": "prof_hahne_en",           // or "prof_hahne_de"
  "language": "en-US",                    // or "de-DE"
  "speed": 1.0,                          // 0.5 = slow, 2.0 = fast
  "format": "mp3",                       // mp3, wav, ogg
  "word_timestamps": true                // optional — for lip-sync
}
```

**Response (success — 200 OK):**
```json
{
  "audio_url": "https://voice-agent.hfu.edu/api/audio/abc123.mp3",
  "duration_seconds": 8.42,
  "format": "mp3",
  "word_timestamps": [
    {"word": "Neural", "start": 0.0, "end": 0.62},
    {"word": "Radiance", "start": 0.62, "end": 1.15},
    {"word": "Fields", "start": 1.15, "end": 1.58},
    ...
  ]
}
```

**Response (error — 4xx/5xx):**
```json
{
  "error": "voice_not_found",
  "message": "Voice ID 'prof_hahne_en' does not exist. Available: ['prof_hahne_en', 'prof_hahne_de']"
}
```

---

## Alternative: Simple File Upload

If a full API is not available, a simpler contract also works:

### `POST /speak` — Returns audio directly

**Request headers:**
```
Content-Type: application/json
Authorization: Bearer <API_KEY>   // if auth required
```

**Response:**
- `Content-Type: audio/mpeg` (or `audio/wav`)
- Body: raw audio bytes
- Header: `X-Duration: 8.42` (optional)

**Our pipeline would then:**
1. POST text to `/speak`
2. Save response body to `.mp3`
3. Use `ffprobe` to get duration locally

---

## Integration Points in Our Code

### Current placeholder (to be replaced):

**File:** `scripts/pipeline.py`
**Function:** `generate_tts(text, out_mp3, voice="en-US-AriaNeural")`

```python
def generate_tts(text, out_mp3, voice="en-US-AriaNeural"):
    """Placeholder TTS via edge-tts."""
    run(["edge-tts", "--voice", voice, "--text", text, "--write-media", out_mp3])
```

### Replacement implementation:

```python
import requests

VOICE_API_URL = "https://voice-agent.hfu.edu/api/speak"
VOICE_API_KEY = os.environ.get("VOICE_API_KEY", "")

def generate_tts(text, out_mp3, voice="prof_hahne_en"):
    """Real voice clone via Voice Agent API."""
    response = requests.post(
        VOICE_API_URL,
        json={
            "text": text,
            "voice_id": voice,
            "language": "en-US",
            "format": "mp3",
            "word_timestamps": True
        },
        headers={"Authorization": f"Bearer {VOICE_API_KEY}"},
        timeout=60
    )
    response.raise_for_status()
    
    data = response.json()
    
    # Download audio
    audio_response = requests.get(data["audio_url"], timeout=30)
    audio_response.raise_for_status()
    with open(out_mp3, "wb") as f:
        f.write(audio_response.content)
    
    # Return timestamps for optional advanced lip-sync
    return data.get("word_timestamps", [])
```

---

## What the Voice Agent Team Needs to Provide

### 1. Base URL
```
https://voice-agent.hfu.edu/api/
```
(or whatever domain)

### 2. Authentication
- **Option A:** API key in `Authorization: Bearer <token>` header
- **Option B:** IP allowlist (no key needed from our VPS: `141.28.79.251`)

### 3. Voice Model
We need a **voice clone** of Prof. Hahne in:
- **English** (`prof_hahne_en`) — primary
- **German** (`prof_hahne_de`) — optional, for German-language lectures

**Training data needed:** ~10–30 minutes of clean Prof. Hahne speech recordings

### 4. Response Format Preference

| Priority | Format | Why |
|----------|--------|-----|
| 1 | JSON + audio_url | Best — we can cache, retry, inspect |
| 2 | Raw audio bytes | Simple — direct file save |

### 5. Optional: Word-Level Timestamps

If provided, we can upgrade from **Wav2Lip** (frame-level lip-sync) to **phoneme-level lip-sync** (mouth shape per phoneme). This gives more accurate lip movement.

**Format:**
```json
[
  {"word": "hello", "start": 0.0, "end": 0.45, "phonemes": [
    {"phoneme": "h", "start": 0.0, "end": 0.08},
    {"phoneme": "eh", "start": 0.08, "end": 0.25},
    {"phoneme": "l", "start": 0.25, "end": 0.35},
    {"phoneme": "ow", "start": 0.35, "end": 0.45}
  ]}
]
```

---

## Fallback Options (If Custom API Not Ready)

If a custom voice API is months away, these are acceptable interim solutions:

| Option | Pros | Cons |
|--------|------|------|
| **ElevenLabs API** | High quality, fast setup, good German support | External dependency, paid |
| **Microsoft Azure TTS** | Neural voices, SSML support, custom voice training | Azure account needed |
| **Google Cloud TTS** | WaveNet voices, 40+ languages | GCP account needed |
| **Coqui TTS** | Open source, self-hosted | Requires training data + GPU for cloning |

**Recommended interim:** ElevenLabs with voice cloning — upload 10 min of Prof. Hahne audio, get instant API endpoint.

---

## Questions for Voice Agent Team

1. What is the base URL / endpoint path?
2. What authentication method? (Bearer token, API key, IP allowlist?)
3. What voice IDs will be available?
4. What audio formats are supported? (MP3, WAV, OGG?)
5. Can we get word-level timestamps?
6. What is the rate limit? (requests/minute)
7. What is the max text length per request?
8. Do you need us to chunk long texts, or does the API handle it?

---

## Test Script (for Voice Agent team)

```python
import requests

url = "YOUR_ENDPOINT_HERE"
payload = {
    "text": "This is a test of the voice agent API.",
    "voice_id": "prof_hahne_en",
    "format": "mp3"
}
headers = {"Authorization": "Bearer YOUR_TOKEN"}

r = requests.post(url, json=payload, headers=headers)
print(f"Status: {r.status_code}")
print(f"Response: {r.json() if 'json' in r.headers.get('content-type', '') else 'binary audio'}")
```

---

*Spec maintained by Project 3 team | HFU — Prof. Dr. Uwe Hahne*
