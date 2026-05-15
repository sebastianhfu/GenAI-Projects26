# Projekt 3 — Educational Video Generation System

## Thema

Entwicklung eines Systems zur automatisierten Erzeugung von didaktischen
Erklärvideos im Präsentations-Stil. Ein Avatar-basierter Moderator führt
durch Inhalte, die auf Folien visualisiert werden, und spricht einen
passenden Erklärtext.

## Ziele

- Konzeption einer Orchestrierungspipeline für Erklärvideos
- Planung der Integration externer Dienste (Avatar-Generierung,
  Voice-Cloning)
- Definition von Schnittstellen und Datenflüssen zwischen verteilten
  Komponenten
- Dokumentation möglicher Architekturen, Phasen und offener Fragen
- Sammlung geeigneter Demo-Themen für ein zukünftiges Prototyping

## Status

> **Planungsphase** — Das Projekt befindet sich ausschließlich in der
> Konzeption und Dokumentation. Weder Avatar-Modelle noch Voice-Clones
> wurden trainiert, und keine Videos wurden generiert. Eine spätere
> Implementierung setzt die Klärung der hier dokumentierten offenen
> Fragen und die Verfügbarkeit der externen Dienste voraus.

## Tools und Ressourcen

| Tool / System | Verwendung |
|---------------|-----------|
| Hermes Agent | Orchestrierung, Content-Planung, Skript-Generierung |
| Externer Avatar-Server | Generierung des Moderator-Avatars (Deepfake / NeRF / Bild-zu-Video) |
| Externer Voice-Server | Synthese der gesprochenen Narration (Voice-Cloning / TTS) |
| Python / FastAPI | Backend für Workflow-Orchestrierung (optional, zukünftig) |
| MkDocs / Pandoc / Manim | Folien-Rendering / Export (geplant) |
| FFmpeg | Audio/Video-Komposition (geplant) |

## Ergebnisse

!!! note "Work in Progress"
    Ergebnisse werden hier dokumentiert, sobald das Projekt abgeschlossen
    ist. Aktuell liegt nur die Planungsdokumentation vor.

## Dokumentation

Detaillierte technische Dokumentation findest du unter
[Dokumentation → Projekt 3](../docs/project03.md).
