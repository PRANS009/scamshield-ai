# ScamShield AI 2.0 — Hackathon Submission Package

**Amazon Developer Hackathon 2026 | Alexa+ Track**  
**Project Title:** ScamShield AI 2.0 — Your Intelligent Digital Safety Guardian  
**Tagline:** Verify Before You Trust.  
**Developer:** Prans Jangra  
**GitHub Repository:** https://github.com/PRANS009/scamshield-ai  

---

## A. Project Description

**ScamShield AI 2.0** transforms digital safety from passive, static form scanners into a proactive, conversational AI Guardian. Built for the Alexa+ era, ScamShield empowers students, job seekers, and everyday internet users to investigate suspicious text messages, recruitment scams, upfront fee demands, and malicious web links in real time. 

Rather than treating fraud detection as an opaque black box or inventing false certitudes, ScamShield orchestrates real underlying cybersecurity tools (safe URL parsing, recruiter domain cross-referencing, heuristic signal extraction, and bounded SerpApi public research). It returns grounded, explainable findings, highlights remaining uncertainty, and provides concrete next steps to stop scams before they happen.

---

## B. Problem Statement

Digital fraud, especially student recruitment scams and internship impersonation, has grown rapidly. Scammers craft convincing messages offering remote AI internships, work-from-home roles, or high-stipend positions. Once candidates express interest, scammers introduce urgent payment demands — claiming money is needed for "registration fees", "laptop insurance", or "training certificates".

Traditional security tools fail these victims:
1. **Antivirus & DNS firewalls** do not catch text-based social engineering on WhatsApp or SMS.
2. **Standard LLMs** frequently hallucinate, telling users an offer looks "legitimate" simply because it is politely written, or hallucinating company policies.
3. **Static scanners** lack context, forcing users to start over every time they have a follow-up question.

Users need an empathetic, conversational, evidence-led guardian that understands natural language, uses real investigation tools, and guides them safely.

---

## C. Unique Innovation

1. **Conversational AI Guardian:** A stateful, multi-turn assistant that remembers investigation context, parses complex follow-up questions, and offers clear safety guidance.
2. **Alexa+-Style Multimodal Simulator:** Demonstrates hands-free voice-first fraud investigation using the Web Speech API (STT & TTS), ambient visual state rings, and multimodal card responses.
3. **Real Tool Orchestration:** Real backend tools (`analyze_message`, `analyze_url`, `investigate_job_offer`, `check_recruiter_signals`, `search_public_evidence`) execute validated logic rather than simulated text.
4. **Transparent Uncertainty Standards:** Clearly differentiates heuristic signals from authenticated facts. Never declares an unknown entity "100% verified" or claims heuristic points are calibrated probabilities.
5. **Zero-Trust URL & Content Safeguards:** Server-side SSRF protection prevents fetching internal networks; external messages are treated strictly as untrusted data to prevent prompt injection.

---

## D. Demonstration Video Script (Total: 2 Minutes 40 Seconds)

### [0:00 – 0:20] The Problem
> **[Visual: Rapid montage of realistic WhatsApp messages: "You're selected for Python Intern! Pay ₹1,999 to confirm seat within 30 mins." Red warning badge pulses.]**
> 
> **Speaker:** "Every day, thousands of students and job seekers receive messages like this. They look professional. They sound urgent. And all too often, they end in financial heartbreak. Today’s scammers don’t hack machines — they hack human trust. How do you verify before you trust?"

---

### [0:20 – 0:45] Product Introduction
> **[Visual: Camera transitions to the sleek ScamShield AI 2.0 dashboard, showing the glowing Alexa+ ambient ring and AI Guardian interface.]**
> 
> **Speaker:** "Meet ScamShield AI 2.0 — your intelligent digital safety guardian, built for the Amazon Developer Hackathon Alexa+ track. ScamShield upgrades fraud detection from complex security forms into an effortless, conversational experience you can talk to in your browser or through Alexa+."

---

### [0:45 – 1:45] Live Agent Investigation (Scenario 1 & 2)
> **[Visual: Speaker clicks 'Tap to Speak' or runs Scenario 1. Alexa glowing ring pulses cyan. Assistant responds with voice.]**
> 
> **User Voice:** *"Alexa, can you check whether my internship offer is suspicious?"*
> 
> **Alexa+ Guardian:** *"Sure! Please share the offer message or link. Avoid sharing passwords, OTPs, or sensitive documents."*
> 
> **User Voice:** *"Congratulations! You have been selected for an AI internship. Pay ₹1,999 for verification within 30 minutes to confirm your seat."*
> 
> **[Visual: Live Tool Execution card appears on screen: Intake → analyze_message → investigate_job_offer. Red badge: High Concern 44/100.]**
> 
> **Alexa+ Guardian:** *"High concern detected. This offer demands an upfront verification fee of ₹1,999 under artificial 30-minute urgency. Legitimate companies and universities never charge seat confirmation fees. Do not send money."*

---

### [1:45 – 2:15] Follow-Up & Explainable Evidence Report
> **[Visual: User asks follow-up: 'Explain why this offer is risky' without re-pasting the text. Full Report opens showing evidence sources and recommendations.]**
> 
> **Speaker:** "Notice how the Guardian retains multi-turn context. When we ask follow-up questions, it breaks down the exact heuristic weights. With one click, we can open the complete Evidence Report — viewing public SerpApi search excerpts, domain analysis, and recommended verification steps."

---

### [2:15 – 2:40] Architecture, Impact & Conclusion
> **[Visual: Architecture diagram: React + FastAPI + In-Memory Sessions + Bounded SerpApi Search + Local Rules Fallback.]**
> 
> **Speaker:** "Under the hood, ScamShield runs on FastAPI and React, orchestrating real inspection tools with zero credential leakage and robust SSRF defenses. If external APIs are unavailable, it falls back seamlessly to local rules. 
> 
> ScamShield AI 2.0 brings accessible, transparent cybersecurity to everyone. Verify before you trust. Thank you!"

---

## E. Submission Information

* **Inspiration:** Witnessing students and peers lose hard-earned savings to fake internship offers and deceptive SMS links.
* **What it does:** Offers an interactive conversational safety guardian that detects upfront fees, credential phishing, fake recruiters, and malicious links with transparent evidence.
* **How it was built:** 
  - Frontend: React 19, TypeScript, Vite, Vanilla CSS design system, Web Speech API.
  - Backend: FastAPI, Python 3.11+, Pydantic schemas, SQLite persistence.
  - Research & Intelligence: SerpApi Google search engine, OpenAI-compatible chat orchestration, local heuristic rules engine.
* **Challenges Encountered:** Designing bounded, safe multi-agent tool execution without allowing prompt injection or SSRF vulnerabilities; maintaining conversational state without leaking private user data.
* **Accomplishments:** Building a fully functional Alexa+-style voice and multimodal simulation with zero mocked backends, complete with transparent uncertainty reporting.
* **What was learned:** The power of explainable AI over black-box probabilities. Users make much safer decisions when they see *why* an offer is concerning rather than just a raw number.
