# Dokumentation — Projekt 1 (Bildgenerierung)

## Setup

### Voraussetzungen

- Python 3.10+
- NVIDIA-GPU mit CUDA-Unterstützung (empfohlen, aber nicht zwingend)
- ca. 10 GB freier Speicherplatz

### Installation

```bash
# ComfyUI clonen
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Abhängigkeiten installieren
pip install -r requirements.txt

# Stable Diffusion Modelle herunterladen
# Modelle nach models/checkpoints/ verschieben
```

### Start

```bash
python main.py
# UI öffnet sich unter http://127.0.0.1:8188
```

---

## Workflows

### Basis-Workflow: Text-zu-Bild

1. **Load Checkpoint** — Modell laden (z. B. SDXL)
2. **CLIP Text Encode** — Positive und negative Prompts
3. **KSampler** — Bildgenerierung mit Sampling-Parametern
4. **Save Image** — Ergebnis speichern

### Erweiterte Workflows

- Bild-zu-Bild mit `Load Image` + `VAE Encode`
- Inpainting mit Maskierung
- ControlNet für präzise Kontrolle

---

## Code-Beispiel: Python API

```python
import requests
import json

# ComfyUI API Aufruf
prompt = {
    "3": {
        "inputs": {"text": "a beautiful castle in the clouds, digital art"},
        "class_type": "CLIPTextEncode"
    },
    # ... weitere Nodes
}

response = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": prompt})
print(response.json())
```

---

## Lessons Learned

- **Prompt Engineering** ist entscheidend. Negative Prompts reduzieren Artefakte.
- **Sampling Steps:** 20–30 Steps bieten den besten Kompromiss aus Qualität und Geschwindigkeit.
- **CFG Scale:** 7–8 ist ein guter Ausgangswert.
- Modelle können von [CivitAI](https://civitai.com) bezogen werden.

## Ergebnisse

!!! note "Wird ergänzt"
