# Dokumentation — Projekt 2 (Audio/Videogenerierung)

## Audio-Setup

### Tools

| Tool | Link | Beschreibung |
|------|------|--------------|
| Suno | [suno.ai](https://suno.ai) | Musikgenerierung aus Text |
| Udio | [udio.com](https://udio.com) | Alternative Musik-KI |
| AudioCraft | [GitHub](https://github.com/facebookresearch/audiocraft) | Meta's Open-Source Audio-KI |

### Beispiel: AudioCraft

```bash
pip install audiocraft

# Musikgenerierung
python -m audiocraft.models.musicgen \
  --prompt "upbeat electronic synthwave, 120 bpm" \
  --duration 30
```

## Video-Setup

### Tools

| Tool | Link | Beschreibung |
|------|------|--------------|
| Runway Gen-3 | [runwayml.com](https://runwayml.com) | Text-zu-Video |
| Pika Labs | [pika.art](https://pika.art) | Video-KI |
| AnimateDiff | [GitHub](https://github.com/guoyww/AnimateDiff) | Open-Source Animation |

### FFmpeg Post-Production

```bash
# Video mit Audio synchronisieren
ffmpeg -i video.mp4 -i audio.mp3 -c:v copy -c:a aac output.mp4

# Video schneiden (Sekunde 10 bis 20)
ffmpeg -ss 10 -t 10 -i input.mp4 -c copy output.mp4
```

---

## Lessons Learned

- Audio und Video separat generieren, dann synchronisieren.
- Für konsistente Video-Charaktere: Image Prompts verwenden.
- 24 fps sind ausreichend für die meisten Anwendungen.

## Ergebnisse

!!! note "Wird ergänzt"
