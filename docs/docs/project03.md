# Documentation — Project 3 (Educational Video Generation System)

## Project Description

This project plans a system for the automated creation of didactic explainer
videos in the style of a PowerPoint presentation with a presenter. The idea is
that a user enters a topic and the system produces a complete video in which an
avatar-based presenter explains slide contents.

The presenter avatar is planned to be modelled on **Prof. Dr. Uwe Hahne**, whose
research and teaching focus lies in media informatics, computer graphics,
human–computer interaction, and related fields at Hochschule Osnabrück.
Consequently, the demo topics suggested below are drawn from these subject
areas.

> **Note:** This page describes the planning state only. No implementation, no
> training, and no generation has been performed.

---

## Planned System Architecture

The architecture is designed as a distributed system in which Hermes acts as
the orchestration agent and coordinates multiple external services.

### Data Flow (planned)

```
┌─────────────────┐
│     User        │  Enters a topic (e.g. "How does 3D rendering work?")
└────────┬────────┘
         ▼
┌─────────────────┐
│  Hermes Agent   │  Creates outline, slide text, and narration script
└────────┬────────┘
         ▼
┌─────────────────┐     ┌──────────────────────┐
│  Voice Server   │◄────│ Audio file (spoken script)
│  (external)     │     │ Format still to be clarified: WAV? MP3? AAC?
└────────┬────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────┐     ┌──────────────────────┐
│  Avatar Server  │◄────│ Video of speaking avatar
│  (external)     │     │ Format still to be clarified: MP4? WebM? Raw image sequence?
└────────┬────────┘     └──────────────────────┘
         │
         ▼
┌─────────────────┐
│  Composition    │  Combines slides, avatar video, and audio into
│  Pipeline       │  a final explainer video (planned, not implemented)
└────────┬────────┘
         ▼
┌─────────────────┐
│  Final Video    │  Output: synchronised presentation video
└─────────────────┘
```

### Currently Available

- Hermes Agent as the orchestration system (running)
- Basic concept idea and this planning documentation

### Not Yet Available / Future

- **Voice Server:** Still to be provided and connected
- **Avatar Server:** Still to be provided and connected
- **Composition Pipeline:** Not yet implemented
- **Slide Rendering Engine:** Not yet selected (Manim, Reveal.js,
  Pandoc-beamer, etc.)

---

## Integration of External Services (Planning)

Since the avatar and voice systems are intended to run on separate servers,
interfaces must be planned. The following communication approaches are
conceivable:

| Approach | Description | Open Questions |
|----------|-------------|----------------|
| **REST API** | Synchronous HTTP request with audio/video as response | Maximum file size? Timeout for long generation? |
| **WebSocket API** | Stream-based transmission for real-time feedback | Do the servers support streaming? |
| **Job Queue** | Async model: submit job → poll status → fetch result | Which queue mechanism? Redis? RabbitMQ? Custom system? |
| **Polling for Job Status** | Combined with REST: POST to start, GET for status, GET for result | How long is a job retained? Retry logic? |
| **Shared Storage** | Generated files placed in shared storage (NFS, S3, SMB) | Who handles cleanup of old files? |
| **File Upload/Download Endpoints** | Explicit upload/download URLs per job | Authentication per endpoint? URL expiry? |

### Recommended Direction (Preliminary)

A **job-queue model with REST polling** seems most robust for generation tasks,
since avatar and voice generation are not instantaneous. The final choice,
however, depends on the capabilities of the external servers.

---

## Open Technical Questions

The following points must be clarified before implementation can begin.

### Voice Server

1. Which API does the voice server expose? (REST, gRPC, WebSocket?)
2. Which authentication is expected? (API key, OAuth, token?)
3. Which input format does the server need? (Plain text? SSML? Prosody markup?)
4. Which output formats does the server deliver? (WAV, MP3, OGG, FLAC? Which bitrate?)
5. Is there a length limit per request? (Characters, words, seconds?)
6. Is batch processing possible, or only individual sentences?

### Avatar Server

1. Which API does the avatar server expose?
2. Does the server need only an audio file as input (audio-driven lip-sync), or also:
   - A prompt / control text?
   - A reference image of the avatar?
   - A face mesh / 3D model?
   - A video as style reference?
3. Which output formats does the server deliver? (MP4, WebM, image sequence as ZIP?)
4. Which resolution and frame rate are achievable?
5. How long does generation take per minute of audio? (Important for timeout planning)
6. Are multiple avatars / persons supported, or only a specific one?

### Data Flow & Infrastructure

7. How are generated assets transferred between servers? (Base64 in JSON? URL? Shared storage?)
8. Where is the final video rendered? (Locally on the Hermes machine? On a dedicated render server?)
9. Which latency is acceptable for an interactive experience? (Minutes? Hours?)
10. How are errors in the pipeline handled? (Retry? Fallback to default voice / default avatar?)
11. Are there storage or bandwidth constraints between the servers?

### Legal and Ethical Questions

12. Which consent documentation exists for the avatar used (Prof. Dr. Uwe Hahne)?
13. Which licence conditions apply to the generated videos? (Own? The external services'?)
14. Which notices must be included in generated videos? ("AI-generated", "Voice clone", etc.)
15. Are there restrictions on public publication of such videos?

### Slides & Content

16. Which tool should render slides? (Manim for mathematical animations? Reveal.js for web slides? Pandoc for static PDFs?)
17. How are slide contents synchronised with the audio script? (Timestamps? Chapter markers?)
18. Should the avatar appear only in the foreground, or should slides also be visible in the background?

---

## Suggested Presentation Topics

For later prototyping, topics should be short enough for a demo video (approx.
1–3 minutes) but technically substantial enough to demonstrate the usefulness
of the system. The topics below are aligned with the research and teaching
areas of **Prof. Dr. Uwe Hahne** — primarily **media informatics, computer
graphics, human–computer interaction, web/mobile technologies, and AI
fundamentals**.

### Topic Categories

- Computer Graphics and Visualisation
- Human–Computer Interaction (HCI)
- Virtual and Augmented Reality
- Web and Mobile Technologies
- Artificial Intelligence and Machine Learning Fundamentals
- Game Development and Interactive Media

### Concrete Topic Suggestions

| No. | Topic | Why It Fits Prof. Hahne's Areas |
|-----|-------|--------------------------------|
| 1 | **How does 3D rendering work?** | Core computer graphics topic |
| 2 | **What is ray tracing?** | Classic graphics rendering technique |
| 3 | **How does a shader program work?** | GPU graphics pipeline |
| 4 | **What is a polygon mesh?** | 3D modelling fundamentals |
| 5 | **How does texture mapping work?** | Graphics texturing |
| 6 | **What is the rendering pipeline?** | Core graphics concept |
| 7 | **How does augmented reality (AR) work?** | AR/VR fundamentals |
| 8 | **What is the difference between VR and AR?** | Mixed reality concepts |
| 9 | **How does computer animation work?** | Animation principles |
| 10 | **What are skeletal animation and rigging?** | Character animation basics |
| 11 | **What is human–computer interaction (HCI)?** | HCI fundamentals |
| 12 | **How does a touch interface work?** | Interaction design |
| 13 | **What is usability engineering?** | HCI design methodology |
| 14 | **How does a search engine work?** | Web technology / information retrieval |
| 15 | **What is a REST API?** | Web development fundamentals |
| 16 | **How does responsive web design work?** | Modern web technology |
| 17 | **What is a neural network?** | AI fundamentals |
| 18 | **How does image classification work?** | Computer vision basics |
| 19 | **What is the difference between supervised and unsupervised learning?** | ML core concept |
| 20 | **How does a recommendation system work?** | Practical AI application |
| 21 | **What is a game engine?** | Game development fundamentals |
| 22 | **How does real-time physics simulation work in games?** | Interactive media |
| 23 | **What is procedural content generation?** | Game design + AI overlap |
| 24 | **How does motion capture work?** | Animation technology |
| 25 | **What is data visualisation?** | Graphics + HCI overlap |

> **Recommended Prototype Topics:** No. 1, 11, 15, 17, or 21 — these are
> concise, visually supportable, and understandable for a broad audience.

---

## Proposed Development Phases

### Phase 1 — Concept and Requirements

**Goal:** Define clear framework conditions before technical work begins.

- [ ] Define target video format (resolution, frame rate, length, target platform)
- [ ] Identify external services and check their availability
- [ ] Define input and output formats (what does the user enter, what comes out?)
- [ ] Select one prototype topic from the list above
- [ ] Check legal consent for avatar and voice usage

**Result:** Requirements document, selected topic, confirmed service availability.

### Phase 2 — Interface Planning

**Goal:** Define API contracts and data flows between Hermes, the voice server,
and the avatar server.

- [ ] Create API specification for voice server (request/response schema, auth, error codes)
- [ ] Create API specification for avatar server
- [ ] Decide file transfer method (upload URL, shared storage, Base64, etc.)
- [ ] Document expected response formats (Audio: WAV/MP3? Video: MP4/WebM? Metadata?)
- [ ] Define job-status polling schema (how often to poll? Which status codes?)

**Result:** API documentation, OpenAPI/Swagger spec (optional), test cases for each interface.

### Phase 3 — Prototype Pipeline Design

**Goal:** Plan the complete flow from topic to raw video without calling the
real servers.

- [ ] Plan slide generation: How does Hermes turn a topic into structured slides?
- [ ] Plan narration generation: How are slides turned into a fluid speech script?
- [ ] Plan synchronisation: How are slides, audio timing, and avatar video aligned?
- [ ] Define fallback strategies: What happens if a server fails or is too slow?

**Result:** Architecture document, sequence diagram, error-handling concept.

### Phase 4 — Future Implementation

**Goal:** Implement the planned pipeline with real services.

> **Note:** This phase requires completion of Phases 1–3 and the external
> servers to be operational.

- [ ] Implement voice-server integration
- [ ] Implement avatar-server integration
- [ ] Implement video composition pipeline (slides + avatar + audio)
- [ ] Test with real generated assets
- [ ] Iterate and refine based on test results

**Result:** Working prototype that produces a demo video for the topic selected in Phase 1.

---

## Lessons Learned

> *To be added once Phases 1–3 are completed and initial insights are
> available.*

## Results

!!! note "Work in Progress"
    Results will be documented here once the project is completed.
    At present only the planning documentation is available.
