# ScamShield AI 2.0 — Your Intelligent Digital Safety Guardian

**Amazon Developer Hackathon 2026 | Alexa+ Track**
**Tagline:** *Verify Before You Trust.*
**Owner:** Prans Jangra
**GitHub Repository:** [https://github.com/PRANS009/scamshield-ai](https://github.com/PRANS009/scamshield-ai)

---

## 🛡️ Project Overview

**ScamShield AI 2.0** upgrades scam detection from static, form-based scanners into an interactive, conversational digital safety companion. Designed for students, job seekers, and digital citizens, ScamShield provides real-time fraud investigation for suspicious messages, upfront fee demands, recruiter impersonation, fake internships, and phishing links.

Unlike black-box AI tools that invent answers or guess credibility, ScamShield orchestrates real underlying cybersecurity tools, executes controlled external research, and delivers grounded, explainable assessments with transparent uncertainty.

---

## 🚨 Problem Being Solved

Online recruitment and communication scams have skyrocketed. Fraudsters target students with realistic-looking AI internship offers or work-from-home roles, demanding upfront "registration", "laptop deposit", or "verification" fees under intense artificial urgency. Traditional cybersecurity tools don't inspect text messages or social chats, while general-purpose chatbots frequently hallucinate or give dangerous advice.

ScamShield AI solves this with an empathetic, multi-turn AI Guardian that:
- Inspects text, links, and documents using validated heuristic rules.
- Gathers external public evidence safely without exposing user messages.
- Retains session context so users can ask natural follow-up questions.
- Simulates an Alexa+ voice and multimodal safety experience.

---

## 🏗️ Architecture

```
+----------------------------------------------------------------------------------+
|                               Client Surfaces                                    |
|   +-----------------------+   +------------------------+   +------------------+  |
|   |  AI Guardian Chat     |   |   Alexa+ Simulator     |   | Dedicated Scanners| |
|   |  (Multi-Turn Sessions)|   | (Web Speech STT / TTS) |   | (URL, Job, QR)   |  |
|   +-----------+-----------+   +-----------+------------+   +--------+---------+  |
+---------------|---------------------------|-------------------------|------------+
                |                           |                         |
                v                           v                         v
+----------------------------------------------------------------------------------+
|                            FastAPI Backend (v2.0.0)                              |
|   +--------------------------------------------------------------------------+   |
|   |                      Agent Orchestration Layer                           |   |
|   |   GuardianManager: In-Memory Multi-Turn Sessions & Context Retention     |   |
|   |   Intent Detector: Greetings, Job Scans, URL Analysis, Follow-ups        |   |
|   +------------------------------------+-------------------------------------+   |
|                                        |                                         |
|                                        v                                         |
|   +--------------------------------------------------------------------------+   |
|   |                       Real Investigation Tools                           |   |
|   |   • analyze_message         • analyze_url          • investigate_job     |   |
|   |   • check_recruiter_signals • search_public_evid.  • generate_safety_rep |   |
|   +---------+--------------------------+-----------------------+-------------+   |
|             |                          |                       |                 |
|             v                          v                       v                 |
|   +--------------------+     +-------------------+   +--------------------+      |
|   | Heuristic Rules    |     | Bounded SerpApi   |   | Optional LLM Ground|      |
|   | Engine (risk.py)   |     | Search (Google)   |   | (OpenAI-compatible)|      |
|   +--------------------+     +-------------------+   +--------------------+      |
+----------------------------------------------------------------------------------+
```

---

## ⚡ Technologies Used

* **Frontend:** React 19, TypeScript, Vite, Vanilla CSS design system, Lucide icons, Recharts, Web Speech API.
* **Backend:** FastAPI, Python 3.11+, Pydantic v2 schemas, SQLAlchemy, SQLite, Uvicorn.
* **External APIs (Configured via backend `.env`):**
  - **SerpApi:** Google Search and Google Jobs research.
  - **OpenAI-compatible LLM:** Optional live conversational synthesis.
* **Security Standards:** RFC 1918 private address filtering (SSRF defense), untrusted content isolation, memory-only file processing.

---

## 🌟 What's New in ScamShield AI 2.0

1. **Conversational AI Guardian (`/guardian`):** Stateful multi-turn chat assistant with live tool execution cards, risk badges, suggested prompts, and copyable answers.
2. **Alexa+-Style Simulator (`/alexa-simulator`):** Browser-based voice/multimodal simulation with animated glowing ring, voice synthesis (TTS), microphone recognition (STT), and one-click demo scenarios.
3. **Real Tool Orchestration:** 6 modular backend tools invoked with validated inputs (`analyze_message`, `analyze_url`, `investigate_job_offer`, `check_recruiter_signals`, `search_public_evidence`, `generate_safety_report`).
4. **Session Context Retention:** Retains active investigation reports so users can ask follow-ups (*"Explain why this offer is risky"*) without re-submitting content.
5. **3 Repeatable Judge Demo Scenarios:** One-click automated tests for Fake Internship Offer, Suspicious Link, and Uncertain Job Offer.
6. **Local Rules-based Guardian Mode:** Transparent fallback ensuring full functionality even when no external API keys are configured.
7. **Premium Cyber Defense UI:** Deep navy/charcoal obsidian theme with emerald and electric blue luminous accents.

---

## 🛡️ Preserved Features from 1.0

* **URL Scanner:** Normalizes URLs and inspects domains, punycode, and HTTP risks safely without opening links.
* **Message & Email Analyzer:** Evaluates text for upfront payment demands, credential theft, and urgency.
* **InternshipShield & JobShield:** Evaluates recruiter domains, stipend fairness, and contract terms.
* **Evidence Desk:** Bounded SerpApi public search retrieving citations and identifying fee-policy contradictions.
* **Career Tools:** Resume keyword matching, career roadmap, and application tracker with text diffs.
* **Report Export:** Comprehensive PDF and JSON report generation.

---

## 🚀 Installation & Local Startup

### Prerequisites
- **Python 3.11+** (Python 3.12 recommended)
- **Node.js 18+** & **npm** (for frontend development/build)

### 1. Clone & Configure Environment

```bash
git clone https://github.com/PRANS009/scamshield-ai.git
cd scamshield-ai
cp .env.example .env
```

Edit `.env` to configure your API keys (optional; local mode works without them):
```dotenv
SERPAPI_API_KEY=your_serpapi_key_here
LLM_API_KEY=your_openai_or_groq_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
```

### 2. Start Backend (Terminal 1)

**Mac / Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

**Windows:**
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Start Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173** in your browser.

---

## 🧪 Running Tests

### Backend Test Suite
```bash
cd backend
python3 -m pytest tests/test_agent.py -v
```

### Frontend Production Build
```bash
cd frontend
npm run build
```

---

## 🎯 Hackathon Judge Demo Walkthrough

Navigate to **http://127.0.0.1:5173/alexa-simulator** and test the 3 pre-loaded scenarios:

1. **Scenario 1 (Fake Internship Offer):** Click *Run Demo*. The agent invokes `investigate_job_offer`, flags the upfront payment demand (₹1,999) and 30-minute urgency, and assigns a High Concern rating.
2. **Scenario 2 (Suspicious Link):** Click *Run Demo*. The agent invokes `analyze_url`, safely normalizes `https://secure-verification.example/login` without opening it, and flags credential theft risk.
3. **Scenario 3 (Uncertain Job Offer):** Click *Run Demo*. The agent explains missing evidence, highlights uncertainty, and asks for the official domain.

---

## ⚠️ Known Limitations

- **No Destination Fetching:** To guarantee user safety, ScamShield never opens, crawls, or executes suspicious URLs.
- **Heuristic Indicators:** Risk scores reflect weighted warning patterns, not a legally binding fraud verdict.
- **Simulation Notice:** The Alexa+ Simulator is a browser-based prototype utilizing the Web Speech API; it is not an official Amazon Echo skill publication.

---

## 📄 License & Attribution

Developed by **Prans Jangra** for the **Amazon Developer Hackathon 2026 (Alexa+ Track)**.
Verify Before You Trust.
