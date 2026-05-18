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
| Hermes Agent (Presentation Agent) | Orchestration, script generation, deepfake generation, final composition |
| External Image Agent | Generation and delivery of reference face images for the avatar (one-time intake per character) |
| External Voice Agent | On-demand voice cloning and text-to-speech synthesis via REST API |
| Python / FastAPI | Backend for workflow orchestration (optional, future) |
| **Reveal.js** + Chrome Headless | HTML slide generation and slide-video rendering |
| **LivePortrait** | Primary deepfake tool — audio-driven single-image talking-head avatar |
| **FFmpeg** | Final overlay composition (slides + avatar + audio → MP4) |
| OpenCV, Pillow | Image validation and preprocessing for avatar intake |

## Results

!!! note "Work in Progress"
    Results will be documented here once the project is completed. At present
    only the planning documentation is available.

## Documentation

Detailed technical documentation can be found at
[Documentation → Project 3](../docs/project03.md).
