# Hopemeals Guardian

Hopemeals Guardian is an AI-driven cyber-forensics platform to **prove, flag, and prevent fraud in donated-food ecosystems**. It combines anomaly detection, image forensics, and a tamper-evident ledger to ensure accountability, transparency, and trust in donation workflows.

---

## Overview

Food donation ecosystems are vulnerable to fraud, tampering, and misuse. Hopemeals Guardian addresses these challenges by:
- Providing a **verifiable evidence ledger** for every donation event.
- Using **machine learning models** to detect anomalies in event patterns.
- Applying **image forensics (ELA)** to flag tampered evidence.
- Enabling **retrieval-based text analysis** to summarize and extract entities from reports.
- Delivering a **dashboard** for investigators to review alerts, timelines, and forensic reports.

---

## Architecture

### Core Components
- **Frontend:** Next.js (React-based dashboard for intake and investigator view)
- **Backend:** FastAPI (Python, REST APIs for ingestion, analysis, ledger verification)
- **Database:** MongoDB (events, metadata), filesystem for evidence storage
- **Ledger:** JSONL append-only hash chain with SHA-256 verification
- **ML/Analysis:**
  - IsolationForest for anomaly detection on event features
  - Error Level Analysis (ELA) for image forgery detection
  - TF-IDF RAG for local text evidence summarization and entity extraction

### Data Flow
1. Events are submitted via API or dashboard intake form.
2. Evidence (images, documents) is uploaded and hashed into the ledger.
3. Analyzer modules (Anomaly, ELA, RAG) process evidence.
4. Alerts are generated and stored.
5. Investigator reviews alerts and verifies ledger integrity via dashboard.

---

## Tech Stack

### Frontend
- Next.js (React, TypeScript)
- Tailwind CSS for styling
- Axios for API requests

### Backend
- FastAPI (Python 3.11)
- Pydantic for validation
- Uvicorn for ASGI server

### Data & Storage
- MongoDB (NoSQL database for events, metadata)
- Local filesystem for evidence storage (demo)
- JSONL hash-chain ledger for tamper-evidence

### Machine Learning / Analysis
- Scikit-learn (IsolationForest anomaly detection)
- Pillow + OpenCV (Error Level Analysis image forensics)
- Scikit-learn TF-IDF + regex (RAG/NLP entity extraction and summaries)

### DevOps & Tooling
- Docker + Docker Compose for reproducible environments
- GitHub Actions CI/CD for automatic docs publishing
- MkDocs + Material for documentation site
- Swagger/OpenAPI auto-generated docs for APIs

---

## Quick Start

```bash
# Clone repo
git clone https://github.com/dhruv-developer/Hopemeals-Guardian.git
cd Hopemeals-Guardian

# Start backend + frontend
docker compose up --build

# Seed with synthetic demo data
python tools/synth_data.py
```

* Frontend: [http://localhost:3000](http://localhost:3000)
* API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## Links

* **Demo Video:** https://www.loom.com/share/26098928535f446897df80ffa68398c6
* **Live Demo:** _[Deployment link coming soon]_

---

## Demo Flow

1. Create Event → `POST /api/events`
2. Upload Evidence → `POST /api/evidence/upload`
3. Verify Ledger → `GET /api/ledger/verify`
4. Run Analyze → `POST /api/analyze/run`
5. View Timeline & Alerts → Dashboard

---

## Documentation

All project documentation is available in the `/docs` directory and published as a static site.

Key references:

* [Runbook](./docs/RUNBOOK.md) – demo and local setup steps
* [Architecture](./docs/ARCHITECTURE.md) – detailed components and diagrams
* [API Reference](./docs/API.md) – endpoints with curated examples
* [Model Cards](./docs/MODEL_CARDS) – anomaly, ELA, RAG/NLP behaviors and limitations
* [SOPs](./docs/SOPs) – evidence intake, image forensics, triage, incident response
* [Security & Privacy](./docs/SECURITY_PRIVACY.md) – RBAC, PII handling, logs

---

## Security & Privacy

* **RBAC:** admin, investigator, field roles (least privilege).
* **PII:** masked or hashed, never logged.
* **Evidence Integrity:** all evidence hashed and chained in JSONL ledger.
* **Data Retention:** raw files TTL configurable; ledger hashes retained.
* **Transport:** HTTPS in production; HTTP local demo only.

---

## Contributing

1. Create a feature branch.
2. Update or add documentation alongside code changes.
3. Submit PR with Conventional Commit messages.

---

---

## Built For

**UST D3CODE 2025 - India Edition**  
Hackathon: https://unstop.com/hackathons/d3code-2025-india-edition-ust-1537313

**Team:**
- Dhruv Dawar
- Shivya Khandpur  
- Sneha Roychowdhury

---

## License

MIT — see [LICENSE](./LICENSE).
