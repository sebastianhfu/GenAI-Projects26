# Image / Avatar Agent API Specification

> **Purpose:** Define the API contract needed from the Image Agent team so that `pipeline.py` can swap out the generic placeholder face for a real Prof. Hahne likeness.
> **Current placeholder:** `assets/avatars/placeholder_face.jpg` — generic public-domain face

---

## What We Need

A **source image** of Prof. Hahne (or a way to generate one) that meets LivePortrait's input requirements:

| Requirement | Specification |
|-------------|---------------|
| **Format** | JPG or PNG |
| **Resolution** | Minimum 512×512, ideally 1024×1024 |
| **Face position** | Centered, frontal or near-frontal |
| **Background** | Neutral or transparent (not critical — LivePortrait crops face) |
| **Lighting** | Even, no harsh shadows |
| **Expression** | Neutral (mouth closed, eyes open) — best for lip-sync base |

---

## Option 1: Static Image File (Simplest)

The Image Agent team provides a single high-resolution portrait image:

```
assets/avatars/prof_hahne.jpg   ← drop-in replacement for placeholder_face.jpg
```

**How we integrate:**
1. Save the image to `assets/avatars/prof_hahne.jpg`
2. Update `pipeline.py` default:
   ```python
   PLACEHOLDER_FACE = "/opt/data/project03-workspace/assets/avatars/prof_hahne.jpg"
   ```
3. Done — pipeline uses it automatically

---

## Option 2: Image Generation API

If the Image Agent provides a generation endpoint (e.g., Stable Diffusion / FLUX / custom model):

### `POST /generate` (or `/avatar`)

**Request:**
```json
{
  "prompt": "Professional headshot portrait of Prof. Dr. Uwe Hahne, frontal view, neutral expression, studio lighting, solid background",
  "style": "photorealistic",
  "width": 1024,
  "height": 1024,
  "format": "jpg",
  "seed": 42                        // optional — for reproducibility
}
```

**Response (success — 200 OK):**
```json
{
  "image_url": "https://image-agent.hfu.edu/api/images/abc123.jpg",
  "width": 1024,
  "height": 1024,
  "format": "jpg",
  "seed": 42
}
```

**Response (error):**
```json
{
  "error": "generation_failed",
  "message": "Face detection failed — image does not contain a detectable face."
}
```

### Integration in pipeline.py

```python
import requests

IMAGE_API_URL = "https://image-agent.hfu.edu/api/generate"
IMAGE_API_KEY = os.environ.get("IMAGE_API_KEY", "")

def fetch_avatar(prompt, out_path):
    """Generate avatar via Image Agent API."""
    response = requests.post(
        IMAGE_API_URL,
        json={
            "prompt": prompt,
            "style": "photorealistic",
            "width": 1024,
            "height": 1024,
            "format": "jpg"
        },
        headers={"Authorization": f"Bearer {IMAGE_API_KEY}"},
        timeout=120
    )
    response.raise_for_status()
    data = response.json()
    
    # Download image
    img_response = requests.get(data["image_url"], timeout=30)
    img_response.raise_for_status()
    with open(out_path, "wb") as f:
        f.write(img_response.content)
    return out_path
```

---

## Option 3: Face Swap / Deepfake API

If the Image Agent team already has a face-swap pipeline:

### `POST /faceswap`

**Request:**
```json
{
  "source_face": "https://image-agent.hfu.edu/faces/prof_hahne_source.jpg",
  "target_video": "https://.../base_avatar_video.mp4",   // optional
  "output_format": "jpg"
}
```

**Use case:** Swap Prof. Hahne's face onto a generic body/avatar template.

---

## LivePortrait Input Constraints

Our deepfake engine ([LivePortrait](https://github.com/KwaiVGI/LivePortrait)) has specific requirements:

| Constraint | Value |
|------------|-------|
| Face detector | RetinaFace (via InsightFace) |
| Min face size | 64×64 pixels |
| Max face size | No hard limit, but 1024×1024 recommended |
| Supported formats | JPG, PNG |
| Color channels | RGB |
| Preferred pose | Frontal or near-frontal |
| Eye state | Open (for better feature extraction) |
| Mouth state | Closed or neutral (best for lip-sync base) |

**What LivePortrait does with the image:**
1. Detects face landmarks (68 points)
2. Extracts identity features (who is this person)
3. Stores facial structure as a latent representation
4. During inference: re-animates the face using driving motion while preserving identity

---

## What the Image Agent Team Needs to Provide

### Minimum viable (Option 1)

Just send us **one high-quality headshot**:
- Resolution: 1024×1024 or higher
- Format: JPG
- Pose: Frontal
- Expression: Neutral
- Background: Any (solid color preferred)

### Ideal (Option 2 or 3)

Provide an API or pipeline that can:
1. Generate consistent Prof. Hahne likeness from text prompt
2. Or swap Prof. Hahne's face onto arbitrary base avatars
3. Return high-resolution (1024+) images
4. Support batch generation (for testing different angles/expressions)

---

## Questions for Image Agent Team

1. **Do you have a high-res portrait photo of Prof. Hahne?** (Option 1)
2. **Or do you have a generative model trained on Prof. Hahne?** (Option 2)
3. **What is the model base?** (Stable Diffusion, FLUX, custom?)
4. **Is there an API endpoint, or do we run inference locally?**
5. **If local:** What are the GPU requirements? Can our RTX A6000 handle it?
6. **Can the model generate multiple angles?** (frontal, 3/4 view, profile)
7. **Can it generate different expressions?** (neutral, smiling, speaking)
8. **What is the output resolution?**

---

## Our Current Setup

### Hardware
- **GPU:** NVIDIA RTX A6000 (48 GB VRAM)
- **VRAM usage during LivePortrait:** ~2–4 GB
- **Headroom available:** ~44 GB for additional image generation models

### Already Installed (via LivePortrait dependency tree)
- **PyTorch 2.7.1+cu118**
- **ONNX Runtime 1.18.0**
- **OpenCV 4.10.0**
- **InsightFace** (face detection + alignment)

### What we can run locally
If the Image Agent provides a **checkpoint / weights file**, we can run inference directly on our GPU:

| Model | VRAM | Speed | Quality |
|-------|------|-------|---------|
| Stable Diffusion 1.5 | ~4 GB | 5s/image | Good |
| Stable Diffusion XL | ~8 GB | 10s/image | Very good |
| FLUX.1-dev | ~24 GB | 30s/image | Excellent |
| Custom LoRA (face-trained) | +2 GB | Same as base | Best for specific face |

**Recommended:** A **SDXL + LoRA** fine-tuned on 10–20 photos of Prof. Hahne. Fast, high quality, easy to deploy.

---

## Interim Fallback Options

If a custom Prof. Hahne model is not ready:

| Option | Pros | Cons |
|--------|------|------|
| **Stock photo + face swap** | Fast, no training | Needs good source photo |
| **D-ID / HeyGen API** | No local GPU needed | External, paid, rate limits |
| **Stable Diffusion + IP-Adapter** | Good face similarity with reference | Needs reference photos |
| **Photo of Prof. Hahne (real)** | Perfect accuracy, zero compute | Needs permission + photo session |

**Recommended interim:** Obtain a real high-quality portrait photo of Prof. Hahne. This is the simplest, most accurate, and requires no model training.

---

## Test Script (for Image Agent team)

```python
import requests

url = "YOUR_ENDPOINT_HERE"
payload = {
    "prompt": "Professional headshot, frontal view, neutral expression",
    "width": 1024,
    "height": 1024
}
headers = {"Authorization": "Bearer YOUR_TOKEN"}

r = requests.post(url, json=payload, headers=headers)
print(f"Status: {r.status_code}")
if r.status_code == 200:
    data = r.json()
    print(f"Image URL: {data.get('image_url')}")
else:
    print(f"Error: {r.text}")
```

---

*Spec maintained by Project 3 team | HFU — Prof. Dr. Uwe Hahne*
