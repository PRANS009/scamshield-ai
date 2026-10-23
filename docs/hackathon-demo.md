# ScamShield AI 2.0 — Hackathon Demonstration Guide

**Amazon Developer Hackathon 2026 | Alexa+ Track**  
**Tagline:** *Verify Before You Trust.*  
**Owner:** Prans Jangra  
**Repository:** https://github.com/PRANS009/scamshield-ai  

---

## 🚀 Quick Launch Instructions

### Backend (Terminal 1)
```bash
cd scamshield-ai/backend
# Python 3.11+
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend (Terminal 2)
```bash
cd scamshield-ai/frontend
npm run dev
```

Open your browser at **http://127.0.0.1:5173** (or port 8000 for the production-bundled FastAPI app).

---

## 🎯 3 Repeatable Judge Demo Scenarios

These three scenarios can be executed instantly with **one click** from the [Alexa+ Simulator](http://127.0.0.1:5173/alexa-simulator) or tested interactively via the [AI Guardian](http://127.0.0.1:5173/guardian).

---

### Scenario 1 — Fake Internship Offer (Upfront Fee Scam)

* **Target Problem:** Thousands of students and early-career job seekers are targeted by fraudulent recruiters demanding "seat confirmation" or "training" fees before starting.
* **Input Text:**
  > `"Congratulations! You have been selected for our AI internship. Pay ₹1,999 for verification within 30 minutes to confirm your seat."`

#### What ScamShield Demonstrates:
1. **Tool Invocation:** Invokes `investigate_job_offer` and `analyze_message`.
2. **Signal Detection:**
   - Detects upfront payment language (`Pay ₹1,999` — 32 heuristic points).
   - Detects artificial urgency pressure (`within 30 minutes` — 12 heuristic points).
   - Detects unverified selection without an interview.
3. **Risk Rating:** Categorized as **High Concern** (Score: 44+/100).
4. **Natural Conversational Explanation:**
   - Explicitly explains that legitimate organizations do not require candidates to pay upfront fees to confirm internship seats.
   - Recommends pausing any payment and verifying the offer through official channels.
5. **Interactive Follow-Up:**
   - Ask: *"Explain why this offer is risky."*
   - Guardian remembers the previous context without asking you to re-paste the message.

---

### Scenario 2 — Suspicious Link (Lookalike Domain & Credential Phishing)

* **Target Problem:** SMS and email messages containing deceptive links designed to harvest user credentials and personal logins.
* **Input Text:**
  > `"I received this message asking me to verify my account at https://secure-verification.example/login"`

#### What ScamShield Demonstrates:
1. **Tool Invocation:** Invokes `analyze_url`.
2. **Safety Protections:**
   - **Never opens or clicks the destination link** on the server or client.
   - Rejects localhost, private IP addresses (RFC 1918), link-local (169.254.x.x), and unsupported schemes (preventing SSRF).
3. **Syntax & Domain Inspection:**
   - Inspects hostname `secure-verification.example`.
   - Explains that the domain does not match any recognized official service.
4. **Actionable Advice:**
   - Advises against submitting credentials on unfamiliar login portals.
   - Highlights that absence of live malicious reports does not guarantee safety.

---

### Scenario 3 — Uncertain Job Offer (Unverified Recruiter & Missing Evidence)

* **Target Problem:** Ambiguous offers from recruiters claiming to represent established companies where no public proof or official website match exists.
* **Input Text:**
  > `"A recruiter offered me a remote internship, but I cannot find the company on its official website. Can you investigate?"`

#### What ScamShield Demonstrates:
1. **Tool Invocation:** Selects bounded research tools and local rule checks.
2. **Missing Evidence Reporting:**
   - Clearly states what is known and what is missing.
   - Asks for helpful additional identifiers (recruiter email domain, company official URL).
3. **Transparent Uncertainty:**
   - Never fabricates legitimacy or fraud conclusions.
   - Explains: *"Search results are leads, not legally authenticated conclusions. Absence of search results does not prove fraud."*

---

## 🎙️ Alexa+-Style Simulator Features

Located at `/alexa-simulator`:

1. **Ambient Visualizer:** Alexa-style cyan/emerald glowing ring that animates when idle, listening, or thinking.
2. **Browser Speech Synthesis (TTS):** Speaks concise, natural answers using the browser's native speech synthesis engine. Can be muted at any time.
3. **Voice Recognition (STT):** Tap "Tap to Speak" to activate the microphone via the Web Speech API. Visual listening state indicates audio capture.
4. **Typed Fallback:** Full keyboard input always available for noisy environments or unsupported browsers.
5. **Report Bridge:** Easily jump from the Alexa+ conversation directly into the full, detailed ScamShield investigation report.
