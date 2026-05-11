# Dokumentation — Projekt 3 (Interaktive Anwendung)

## Architektur

```
Frontend (JavaScript/p5.js)
         │
         ▼
Backend API (FastAPI/Flask)
         │
         ▼
KI-Modell (ONNX Runtime / TensorFlow.js)
```

## Beispiel: Streamlit-App

```python
import streamlit as st
from PIL import Image
import requests

st.title("KI Bildgenerator")

prompt = st.text_input("Prompt eingeben:")

def generate_image(prompt):
    # API-Aufruf an Stable Diffusion
    response = requests.post("http://localhost:7860/sdapi/v1/txt2img", json={
        "prompt": prompt,
        "steps": 20,
        "width": 512,
        "height": 512
    })
    return response.json()["images"][0]

if st.button("Generieren"):
    with st.spinner("Generiere Bild..."):
        image_data = generate_image(prompt)
        st.image(f"data:image/png;base64,{image_data}")
```

## TensorFlow.js: Echtzeit-Stiltransfer

```html
<script src="https://cdn.jsdelivr.net/npm/@tensorflow/tfjs"></script>
<script>
  async function loadModel() {
    const model = await tf.loadLayersModel('model.json');
    // Modell auf Webcam-Bild anwenden
  }
</script>
```

---

## Lessons Learned

- Für Echtzeitanwendungen: Modelle vorher quantisieren (INT8/FP16).
- WebGL-Backend in TensorFlow.js ist deutlich schneller als CPU.
- CORS korrekt konfigurieren, wenn Frontend und Backend getrennt laufen.

## Ergebnisse

!!! note "Wird ergänzt"
