# Project 3 — Educational Video Generation System

## Topic

Development of a system for automated creation of didactic explainer videos in a
presentation-style format. An avatar-based presenter guides through content
visualised on slides and delivers a matching narration.

## Goals

- Conceive an orchestration pipeline for explainer videos
- Plan the integration of external services (avatar generation, voice cloning)
- Define interfaces and data flows between distributed components
- Document possible architectures, phases, and open questions
- Collect suitable demo topics aligned with Prof. Dr. Uwe Hahne's research areas at
  Hochschule Furtwangen University (HFU)

## Status

> **Planning phase only** — This project is exclusively in the conception and
> documentation stage. No implementation, training, or generation has been
> carried out. A later implementation depends on clarifying the open questions
> documented here and on the availability of the external services.

## Tools and Resources

| Tool / System | Purpose |
|---------------|---------|
| Hermes Agent | Orchestration, content planning, script generation |
| External Avatar Server | Generation of the presenter avatar (deepfake / NeRF / image-to-video) |
| External Voice Server | Synthesis of spoken narration (voice cloning / TTS) |
| Python / FastAPI | Backend for workflow orchestration (optional, future) |
| MkDocs / Pandoc / Manim | Slide rendering / export (planned) |
| FFmpeg | Audio/video composition (planned) |

## Results

!!! note "Work in Progress"
    Results will be documented here once the project is completed. At present
    only the planning documentation is available.

## Documentation

Detailed technical documentation can be found at
[Documentation → Project 3](../docs/project03.md).
