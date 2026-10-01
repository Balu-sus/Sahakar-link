# Sahakar-Link 🚀
> **SIH26087** — AI & LMS-Enabled Cooperative Capacity Building, ERP & Employment Ecosystem

Sahakar-Link is a hardware-agnostic, offline-first digital operating system connecting cooperative training end-to-end—from nomination and learning to multi-modal attendance, verified skill profiling, and employment outcomes.

---

## 🏗️ System Architecture

```text
User Apps (Student / Trainer / Admin / Employer)
       │
       ▼
  API Gateway & Security Layer
       │
       ▼
  Application Services (Course, Exam, Certs, Matching, Sync)
       │
       ▼
  AI Orchestrator (FastAPI / LangGraph)
   ├── LLM Service (Qwen2.5-7B-Instruct)
   ├── Vector RAG Pipeline (Llama Nemotron Embed + Reranker)
   ├── Vision & OCR (PaddleOCR)
   ├── Biometrics (AdaFace + Liveness Anti-Spoofing)
   └── Translation (IndicTrans2)
       │
       ▼
  Data Layer (PostgreSQL / Vector DB / Object Storage / SQLite Cache)
