# ScamShield AI 2.0 — Architecture and Trust Boundaries

**Amazon Developer Hackathon 2026 | Alexa+ Track**
**Tagline:** Verify Before You Trust.

```
+----------------------------------------------------------------------------------+
|                               Client Surfaces                                    |
|                                                                                  |
|   +-----------------------+   +------------------------+   +------------------+  |
|   |  AI Guardian Chat     |   |   Alexa+ Simulator     |   | Dedicated Scanners| |
|   |  (Multi-Turn Sessions)|   | (Web Speech STT / TTS) |   | (URL, Job, QR)   |  |
|   +-----------+-----------+   +-----------+------------+   +--------+---------+  |
+---------------|---------------------------|-------------------------|------------+
                |                           |                         |
                v                           v                         v
+----------------------------------------------------------------------------------+
|                            FastAPI Backend (v2.0.0)                              |
|                                                                                  |
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

## 1. System Components

### Frontend (React 19 + TypeScript + Vite)
- **AI Guardian (`/guardian`):** Stateful conversational interface with live tool execution cards, risk indicators, suggested follow-up prompts, and report export.
- **Alexa+-Style Simulator (`/alexa-simulator`):** Voice/multimodal simulation implementing Web Speech API (`SpeechRecognition` and `SpeechSynthesis`) with glowing ambient state ring, audio waveform, and 3 one-click judge demo scenarios.
- **Dedicated Scanner Pages:** Preserved URL scanner, message analyzer, InternshipShield, QR decoder, and offer letter review.
- **Career & Storage Tools:** Resume matcher, career roadmap, application tracker, and local history.

### Backend (FastAPI + Pydantic v2 + SQLite)
- **Agent Orchestrator (`app/agents/guardian.py`):** Manages multi-turn conversation sessions, evaluates user intent, coordinates tools, and generates grounded responses.
- **Tool Suite (`app/agents/tools.py`):** Real, validated backend functions returning structured findings, evidence leads, and limitations.
- **Security & Validation Layer (`app/security/validation.py`):** Strict SSRF protections, URL sanitization, prompt injection defenses, and in-memory file handling.
- **Storage Layer (`app/database/store.py`):** Anonymous capability-token scoped records (reports, applications, snapshots).

---

## 2. Controlled Investigation Tools

All tools accept validated Pydantic inputs and return structured outputs:

| Tool Name | Real Invoked Function | Purpose |
|:---|:---|:---|
| `analyze_message` | `app.services.risk.analyze_rules` | Detects upfront fees, urgency, credential demands, and guarantees. |
| `analyze_url` | `app.security.validation.normalize_url` + `analyze_rules` | Inspects hostnames, punycode, unencrypted HTTP, and brand lookalikes without fetching destination. |
| `investigate_job_offer`| `app.agents.investigator.investigate` | Multi-agent evaluation of role, stipend, contracts, and quality. |
| `check_recruiter_signals`| `app.agents.tools.tool_check_recruiter_signals` | Cross-references recruiter email domains against official company domains. |
| `search_public_evidence`| `app.services.search.search_service.web` | Bounded SerpApi Google search for known recruitment warnings and no-fee policies. |
| `generate_safety_report`| `app.agents.investigator.investigate` | Produces standardized `Report` objects with citation IDs. |

---

## 3. Session Management & Multi-Turn State

The `GuardianManager` maintains in-memory `SessionState`:
- **`session_id`:** Unique UUID per conversation.
- **`messages`:** Chronological record of user inputs, assistant responses, executed tools, and evidence leads.
- **`active_report`:** Automatically stores the most recently generated investigation report.
- **Follow-up Context:** Follow-up questions like *"Why did I get this score?"* or *"What should I do next?"* reference `active_report` directly, eliminating repetitive re-submission.

---

## 4. Security & Privacy Safeguards

1. **Untrusted Data Isolation:** External message text, emails, and web snippets are strictly treated as data payloads, never executed as agent system instructions.
2. **SSRF Rejection:** All submitted URLs undergo strict validation. Private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), localhost (`127.0.0.1`), cloud metadata (`169.254.169.254`), non-HTTP schemes, and invalid ports are rejected.
3. **No Destination Fetching:** ScamShield never opens, crawls, or executes JavaScript on suspicious links.
4. **Credential Privacy:** API keys (`SERPAPI_API_KEY`, `LLM_API_KEY`) stay strictly in backend environment variables.
5. **Session Deletion:** Complete deletion endpoint (`DELETE /api/v1/agent/session/{id}`) allows instant wiping of session data.
