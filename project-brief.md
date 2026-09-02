# Project Brief — CCTV-Based Missing Person Search

**Event:** Dominion Build-a-thon
**Working title:** Netra (alternatives: Trace, Drishti, FindFast)
**Status:** Planning — v1
**Budget:** ₹0. Every tool listed below is free.

---

## 1. The Problem

When a person goes missing, the first few hours matter most. Right now, police collect CCTV footage from nearby shops, traffic signals, and stations, then watch it manually. A single officer reviewing footage from ten cameras over six hours is watching sixty hours of video. It is slow, exhausting, and clues get missed — not because officers are careless, but because human attention degrades after twenty minutes of watching a static frame.

## 2. What We Are Building

A tool where an officer uploads one or two photos of the missing person and a folder of CCTV footage. The system scans every video, finds every face, compares each one against the uploaded photo, and returns a **timeline of sightings** — timestamp, camera location, confidence score, and a short video clip for each hit.

Sixty hours of manual review becomes a few minutes of processing and a page an officer can actually read.

Think of the face-grouping feature in Google Photos, pointed at CCTV footage and built for a search operation.

## 3. How It Works

```
Upload reference photo(s)
        ↓
Generate face embedding (a 512-number fingerprint of the face)
        ↓
Upload CCTV videos
        ↓
Extract frames (1 frame every 0.5s — not every frame, that's wasteful)
        ↓
Detect all faces in each frame
        ↓
Generate embedding for each detected face
        ↓
Compare against reference embedding (cosine similarity)
        ↓
Similarity above threshold → record as a sighting
        ↓
Cut a 10-second clip around that timestamp
        ↓
Render timeline in dashboard
```

The key idea: we never compare images to images. We convert every face into a list of 512 numbers, and comparing two lists of numbers is nearly instant. This is what makes the search fast.

## 4. Tech Stack

Everything here is free and open source. Nothing requires a credit card.

### Machine Learning
| Component | Tool | Why |
|---|---|---|
| Face detection | **InsightFace** (RetinaFace) | Handles small, angled, partially blocked faces — which is what CCTV gives us |
| Face embeddings | **InsightFace** (ArcFace, `buffalo_l` model pack) | State of the art accuracy, runs on CPU, no API cost |
| Vector search | **FAISS** (CPU version) | Searches millions of face vectors in milliseconds |
| Video/frame handling | **OpenCV** + **FFmpeg** | Frame extraction and clip cutting |

> **Licensing note:** InsightFace's pretrained models are released for research and non-commercial use. Fine for a hackathon. If we ever commercialise, we retrain on a permissively licensed dataset. Worth knowing before a judge asks.

### Backend
| Component | Tool |
|---|---|
| API framework | **FastAPI** (Python) |
| Background jobs | FastAPI `BackgroundTasks` — upgrade to **Celery + Redis** only if we need it |
| Database | **PostgreSQL** (via Docker locally, or Supabase free tier) |
| File storage | Local filesystem for the demo — **MinIO** if we want S3-style storage |

### Frontend
| Component | Tool |
|---|---|
| Framework | **React + Vite** |
| Styling | **Tailwind CSS** |
| Video playback | `react-player` or plain HTML5 `<video>` |
| Charts/timeline | **Recharts** |

### Infrastructure
| Component | Tool |
|---|---|
| Containers | **Docker + Docker Compose** |
| Frontend hosting | **Vercel** or **Netlify** (free tier) |
| Backend hosting | **Render** or **Railway** (free tier) — or just run locally for the demo |
| Heavy processing | Our own laptops (CPU is enough) or **Google Colab** free GPU for bulk runs |
| Code | **GitHub** (free private repos) |

### What we are deliberately NOT using
- No paid APIs (AWS Rekognition, Azure Face, Google Vision) — all cost money
- No Kubernetes — unnecessary complexity at this scale
- No Elasticsearch or Neo4j — PostgreSQL handles everything we need
- No LLM APIs — this problem does not need one

## 5. Database Schema (first draft)

```
cases
  id, case_name, created_at, officer_name, status

reference_photos
  id, case_id, image_path, embedding (vector), uploaded_at

videos
  id, case_id, file_path, camera_name, camera_lat, camera_lng,
  recording_start_time, duration_seconds, processing_status

sightings
  id, case_id, video_id, timestamp_in_video, real_world_time,
  confidence_score, cropped_face_path, clip_path, officer_verified (bool)

audit_log
  id, case_id, action, performed_by, timestamp
```

The `audit_log` table is not optional. See section 8.

## 6. Team Split

Adjust to however many of us there are.

**Person A — ML Pipeline (hardest role)**
Frame extraction, face detection, embedding generation, similarity matching, threshold tuning. This person owns accuracy.

**Person B — Backend**
FastAPI endpoints, database schema, file upload handling, job queue, clip generation with FFmpeg.

**Person C — Frontend**
Upload interface, timeline view, sighting cards with face crops, video playback, map view of camera locations.

**Person D — Demo, data, and pitch**
Records our test footage, builds the demo case, writes the pitch, prepares answers to judge questions, handles the ethics/privacy story.

If we are only three, Person D's work splits across everyone — but somebody must own it. Teams lose because their demo data is bad, not because their code is bad.

## 7. Build Plan

**Stage 1 — Core pipeline (do this first, nothing else matters until it works)**
Get a Python script that takes one photo and one video and prints timestamps where the person appears. Command line only. No API, no UI.

**Stage 2 — Wrap it in an API**
FastAPI endpoints for creating a case, uploading photos and videos, triggering a scan, and fetching results. Database wired in.

**Stage 3 — Dashboard**
Upload screen, processing status, timeline of sightings with face crops and clips, map of camera locations.

**Stage 4 — Demo prep**
Record our footage, run the full flow end to end at least five times, rehearse the pitch, prepare failure recovery (see section 10).

**Rule:** if we are behind schedule, Stage 4 does not get cut. Stage 3 gets simpler instead.

## 8. Privacy and Ethics — Not Optional

A judge *will* ask "how is this not mass surveillance?" We need a real answer, built into the product, not a slide.

Our design rules:
1. **Case-bound search.** A scan can only run against a registered missing person case. There is no "search for any face" mode.
2. **Non-matches are discarded.** Faces that do not match the reference are never stored — the embedding is computed, compared, and thrown away in memory. We do not build a face database.
3. **Every action is logged.** Who searched, for which case, when, on what footage.
4. **Human confirmation required.** The system produces *candidates*, never conclusions. An officer marks each sighting confirmed or rejected. We say this out loud in the pitch.
5. **Confidence is always visible.** Every result shows its score. We never present a match as certain.

Teams that have thought about this beat teams that have not.

## 9. Demo Data — Read This Carefully

**We record our own footage.** Team members walk past phone cameras placed at three or four locations around campus, at known times. We use our own faces.

**We do not use real CCTV footage, real missing person cases, or strangers' faces.** It is a legal problem and it will sink the pitch if a judge notices.

Get consent in writing from anyone who appears in the footage, even teammates. Takes two minutes, looks extremely professional if asked.

## 10. Known Risks

| Risk | Reality | Mitigation |
|---|---|---|
| **CCTV face quality** | Real CCTV faces are small, blurry, side-angle. Accuracy drops hard compared to clean photos. **This is our biggest risk.** | Tune the similarity threshold on our actual test footage, not on clean portraits. Budget real time for this. |
| False positives | Similar-looking people will match | Show confidence scores, require officer verification, tune the threshold to favour recall over precision — better to show ten candidates than miss the person |
| Processing speed | Long videos take time on CPU | Sample frames at 0.5s intervals, resize frames before detection, process videos in parallel |
| Demo fails live | Live processing on stage is risky | Pre-process everything before the pitch. Have a recorded backup video of the working demo. Never process live unless we have run it successfully ten times. |
| Scope creep | Someone will suggest adding gait recognition or clothing detection | The answer is no. One thing, working well. |

## 11. What We Are NOT Building

Saying this clearly saves us from ourselves:

- No live camera streaming — we work with uploaded footage
- No person re-identification by clothing or body shape
- No mobile app
- No user accounts or role management beyond a hardcoded demo login
- No real police system integration

If we finish everything else early, we can revisit. We will not finish early.

## 12. The Pitch in One Line

> Sixty hours of CCTV footage, searched in minutes, so police can act during the hours that actually matter.

---

**Next step for the team:** everyone install Python 3.10+, Docker, and Node.js. Person A starts Stage 1 immediately — nothing else can be tested until the core pipeline produces a match.
