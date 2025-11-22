# PatentPulse

PatentPulse is a resilient, high-concurrency document ingestion and analysis pipeline designed to process unstructured, potentially corrupted legal documents ("toxic data") without destabilizing core infrastructure. It demonstrates defensive engineering principles for high-availability AI-powered document analysis.

## Executive Summary

PatentPulse leverages Go for high-performance ingestion and Python/AI for semantic risk analysis, orchestrated via a Circuit-Breaker architecture to ensure 99.99% availability—even when downstream AI models hang or fail.

**Key Differentiator:** Unlike standard parsers that crash on bad input, PatentPulse uses "Defensive Architecture" to validate, sanitize, and gracefully degrade under load.

## System Architecture

- **Frontend (React + Tailwind):** Zero-Trust UI with optimistic updates and clear error states ("AI Busy" vs "Network Error").
- **Gateway Service (Go):** Defensive shield for file uploads, stream limiting, memory protection, and worker pool management.
- **Intelligence Service (Python):** The "Brain" for NLP/LLM risk scoring and keyword extraction.
- **Communication:** Synchronous HTTP/gRPC with strict context timeouts.

## Core Features & Functional Requirements

### Defensive Ingestion (The "Shield")
- Accepts text/PDF uploads via REST API
- Rejects files >10MB immediately (streamed, not buffered)
- Enforces strict concurrency (max 3 parallel jobs), load shedding with 503

### Resilient Analysis (The "Brain")
- Go service calls Python AI service for analysis
- Circuit breaker: cancels requests >5s, returns fallback/partial result
- Analysis result includes `Risk Score` (0-100) and `Keywords`

### Honest User Interface
- UI displays non-blocking "Processing" state
- If AI times out, UI shows yellow warning ("Analysis Delayed")

## API Contracts

### POST /upload (Go Gateway)
- **Input:** `multipart/form-data` (File)
- **Output (200 OK):**
  ```json
  {
    "job_id": "uuid-1234",
    "status": "completed",
    "risk_score": 85,
    "keywords": ["Infringement", "Liability", "Pending"],
    "warning": null
  }
  ```
- **Output (503):**
  ```json
  {"error": "System under high load, please retry in 10s"}
  ```

### POST /analyze (Python AI Service)
- **Input:** `{ "content": "raw text string..." }`
- **Output:** `{ "score": 85, "entities": ["US Patent 998...", "Google"] }`

## Tech Stack
- **Backend:** Go (Golang)
- **AI Service:** Python (FastAPI)
- **Frontend:** React (Vite + Tailwind)

## Setup & Usage

1. **Go Backend:** See `main.go` for defensive ingestion and circuit breaker logic.
2. **Python AI Service:** See `brain.py` for FastAPI-based analysis with chaos mode.
3. **React Dashboard:** See `App.jsx` for upload UI and risk visualization.

## License
See [LICENSE](LICENSE) for details.
