"""ScamShield AI 2.0 - Guardian Agent Orchestrator

Manages multi-turn conversation sessions, intent recognition, real tool invocation,
and grounded, explainable fraud guidance for the AI Guardian & Alexa+ Simulator.
"""
import re
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.schemas.core import Investigation, Report
from app.agents.tools import (
    tool_analyze_message,
    tool_analyze_url,
    tool_investigate_job_offer,
    tool_check_recruiter_signals,
    tool_search_public_evidence,
    tool_generate_safety_report,
    get_tool_definitions
)
from app.services.llm import explain
from app import config
from app.security.validation import redact

class MessageItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: str # 'user' | 'assistant'
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    tools_executed: List[Dict[str, Any]] = []
    risk_level: Optional[str] = None
    risk_score: Optional[int] = None
    findings: List[str] = []
    evidence_leads: List[Dict[str, Any]] = []
    uncertainty: Optional[str] = None
    suggested_prompts: List[str] = []

class SessionState(BaseModel):
    session_id: str
    created_at: str
    updated_at: str
    messages: List[MessageItem] = []
    active_report: Optional[Dict[str, Any]] = None
    active_context: Dict[str, Any] = {}

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=25000)
    session_id: Optional[str] = None
    research_consent: bool = False
    ai_consent: bool = False
    company: Optional[str] = None
    official_domain: Optional[str] = None
    recruiter_email: Optional[str] = None

class ChatResponse(BaseModel):
    session_id: str
    assistant_message: str
    tools_executed: List[Dict[str, Any]]
    findings: List[str]
    evidence_sources: List[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    uncertainty: str
    suggested_next_steps: List[str]
    suggested_prompts: List[str]
    report: Optional[Dict[str, Any]]
    mode: str

class GuardianManager:
    """Thread-safe, privacy-aware in-memory session manager for Guardian conversations."""
    def __init__(self):
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> SessionState:
        now_iso = datetime.now(timezone.utc).isoformat()
        if session_id and session_id in self._sessions:
            sess = self._sessions[session_id]
            sess.updated_at = now_iso
            return sess
        new_id = session_id if (session_id and len(session_id) >= 8) else str(uuid.uuid4())
        sess = SessionState(
            session_id=new_id,
            created_at=now_iso,
            updated_at=now_iso,
            messages=[],
            active_report=None,
            active_context={}
        )
        self._sessions[new_id] = sess
        return sess

    def get(self, session_id: str) -> Optional[SessionState]:
        return self._sessions.get(session_id)

    def delete(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

guardian_store = GuardianManager()

def is_greeting_or_inquiry(text: str) -> bool:
    """Identifies conversational greetings or inquiry prompts before inputting suspicious data."""
    t = text.lower().strip()
    greetings = [
        "hi", "hello", "hey", "help", "who are you", "what can you do", "good morning",
        "good afternoon", "good evening", "alexa"
    ]
    if t in greetings:
        return True
    inquiry_patterns = [
        r"^can you check (?:whether|if) (?:my|an|this|the) (?:internship|job|offer|letter|link|message|\s)+ is (?:suspicious|fake|legit|real)",
        r"^can you (?:check|investigate|verify|analyze) (?:whether|if|my|an|this|the|\s)+ (?:suspicious|fake|legit|real)",
        r"^is this (?:internship|job|offer|opportunity|\s)+ (?:genuine|fake|real|legit)\??$",
        r"^how do i verify (?:a|an|the) (?:internship|offer|recruiter|link)\??$",
        r"^what should i do if a recruiter asks for money\??$"
    ]
    return any(re.search(pat, t) for pat in inquiry_patterns)

def is_followup_question(text: str, has_active_report: bool) -> bool:
    """Checks if the user's message is asking a follow-up about an already analyzed report."""
    if not has_active_report:
        return False
    t = text.lower().strip()
    followup_patterns = [
        r"\b(?:why|explain|tell me more|how come)\b",
        r"\b(?:score|risk|level|points|indicators)\b",
        r"\b(?:source|evidence|snippets|google|search)\b",
        r"\b(?:next step|what should i do|is it safe|should i pay|can i pay)\b",
        r"\b(?:refund|guarantee|fake|scam|warning)\b"
    ]
    return any(re.search(pat, t) for pat in followup_patterns)

async def process_chat(req: ChatRequest) -> ChatResponse:
    """Main orchestrator for ScamShield AI Guardian conversations."""
    session = guardian_store.get_or_create(req.session_id)
    text = req.message.strip()

    # Log user turn
    # Conversation history is transient, but it still must not retain secrets a
    # user may accidentally paste. The current turn remains in memory only long
    # enough to run the local investigation tools below.
    user_turn = MessageItem(role="user", content=redact(text))
    session.messages.append(user_turn)

    tools_run: List[Dict[str, Any]] = []
    findings: List[str] = []
    evidence_sources: List[Dict[str, Any]] = []
    suggested_steps: List[str] = []
    risk_assessment: Optional[Dict[str, Any]] = None
    report_dict: Optional[Dict[str, Any]] = session.active_report
    uncertainty = "Independent verification is always required. Screening heuristics do not guarantee safety."

    # 1. Greeting or Initial Inquiry
    if is_greeting_or_inquiry(text):
        assistant_text = (
            "Hello! I am your ScamShield AI Guardian. "
            "Please share the suspicious message, email, offer letter, or website link you'd like me to investigate. "
            "For your safety, please avoid pasting personal passwords, OTPs, or bank account numbers."
        )
        suggested_prompts = [
            "Congratulations! You have been selected for an internship. Pay ₹1,999 to confirm your seat.",
            "I received a message asking me to verify my account at https://secure-verification.example/login",
            "A recruiter offered me a remote internship, but I cannot find the company on its official website. Can you investigate?",
            "Can you investigate this suspicious URL?"
        ]
        resp = ChatResponse(
            session_id=session.session_id,
            assistant_message=assistant_text,
            tools_executed=[],
            findings=["Guardian active and waiting for content to inspect."],
            evidence_sources=[],
            risk_assessment=None,
            uncertainty="No content has been inspected yet.",
            suggested_next_steps=["Paste an offer letter, text message, or web link to begin."],
            suggested_prompts=suggested_prompts,
            report=None,
            mode="AI Guardian Ready"
        )
        session.messages.append(MessageItem(role="assistant", content=assistant_text, suggested_prompts=suggested_prompts))
        return resp

    # 2. Follow-up to an existing investigation
    if is_followup_question(text, bool(session.active_report)):
        rep = session.active_report
        t_low = text.lower()
        if "score" in t_low or "risk" in t_low or "why" in t_low:
            flags_summary = "; ".join(f"{f['label']} (+{f['points']} pts)" for f in rep.get("red_flags", []))
            assistant_text = (
                f"This investigation resulted in a {rep.get('risk_level', 'Moderate')} concern rating "
                f"with a heuristic score of {rep.get('risk_score', 0)}/100. "
                f"Key observed signals include: {flags_summary or 'No specific high-severity red flags'}. "
                f"Remember, this score reflects heuristic warning patterns, not a legally binding fraud conviction."
            )
        elif "evidence" in t_low or "source" in t_low:
            sources = rep.get("sources", [])
            assistant_text = (
                f"We gathered {len(sources)} public search excerpts. "
                f"{' '.join(rep.get('unverified_claims', []))} "
                f"Always visit official company portals independently rather than clicking links provided in messages."
            )
        elif "pay" in t_low or "money" in t_low or "fee" in t_low:
            assistant_text = (
                "Do not make any upfront payments or fee transfers. Legitimate employers, universities, "
                "and reputable internships do not require candidates to pay 'seat reservation', 'processing', "
                "or 'laptop delivery' fees before joining."
            )
        else:
            assistant_text = (
                "Here are the recommended safety actions based on your investigation:\n"
                + "\n".join(f"• {rec}" for rec in rep.get("recommendations", []))
            )

        resp = ChatResponse(
            session_id=session.session_id,
            assistant_message=assistant_text,
            tools_executed=[{"tool": "session_context_lookup", "status": "success", "report_id": rep.get("report_id")}],
            findings=[f"Referenced active report {rep.get('report_id')[:8]}"],
            evidence_sources=rep.get("sources", []),
            risk_assessment={
                "level": rep.get("risk_level"),
                "score": rep.get("risk_score"),
                "reasons": [f["label"] for f in rep.get("red_flags", [])]
            },
            uncertainty="Deterministic follow-up based on your active investigation report.",
            suggested_next_steps=rep.get("recommendations", []),
            suggested_prompts=["Explain why this offer is risky.", "What should I do next?", "Can you check another message?"],
            report=rep,
            mode="Local Rules-based Guardian (Session Context)"
        )
        session.messages.append(MessageItem(role="assistant", content=assistant_text))
        return resp

    # 3. New Content Investigation
    has_url = bool(re.search(r"https?://[^\s<>\"\)]+", text))
    is_job_or_internship = any(w in text.lower() for w in ["intern", "job", "hiring", "recruiter", "stipend", "salary", "seat", "offer", "interview"])
    
    # Route tool execution
    if has_url and not is_job_or_internship:
        url_match = re.search(r"https?://[^\s<>\"\)]+", text)
        target_url = url_match.group(0) if url_match else text
        url_result = await tool_analyze_url(target_url)
        tools_run.append(url_result)
        
        if url_result.get("status") == "success":
            findings.extend([f"Observed domain: {url_result['hostname']}"])
            if url_result["red_flags"]:
                findings.extend([f"{f['label']}: {f['explanation']}" for f in url_result["red_flags"]])
            risk_assessment = {
                "level": url_result["risk_level"],
                "score": url_result["risk_score"],
                "reasons": [f["label"] for f in url_result["red_flags"]]
            }
            rep_res = await tool_generate_safety_report("url", target_url)
            report_dict = rep_res["report"]
            session.active_report = report_dict
            tools_run.append({"tool": "generate_safety_report", "status": "success"})
            
            assistant_text = (
                f"I inspected the URL **{url_result['hostname']}** safely without opening the destination page.\n\n"
                f"• **Risk Rating**: {url_result['risk_level']} Concern (Heuristic Score: {url_result['risk_score']}/100)\n"
                f"• **Hostname**: `{url_result['hostname']}`\n"
                f"• **Findings**: {'; '.join(f['label'] for f in url_result['red_flags']) if url_result['red_flags'] else 'No obvious heuristic anomalies detected in URL syntax.'}\n\n"
                "**Safety Guidance**: Never enter passwords, credentials, or OTPs on unfamiliar login portals. "
                "Always verify the domain against your bookmarks or official apps."
            )
            suggested_steps = [
                "Do not input credentials or sensitive data on this destination.",
                "Verify the domain directly through an official search engine or bookmark.",
                "Check for lookalike character substitutions or unexpected top-level domains."
            ]
        else:
            assistant_text = f"The URL provided could not be inspected safely: {url_result.get('error', 'Invalid URL')}. {url_result.get('safety_note', '')}"
            suggested_steps = ["Check the URL spelling.", "Avoid clicking unverified links."]

    else:
        # Investigate as message or internship/job offer
        company_hint = req.company or session.active_context.get("company", "")
        off_domain = req.official_domain or session.active_context.get("official_domain", "")
        rec_email = req.recruiter_email or session.active_context.get("recruiter_email", "")

        job_result = await tool_investigate_job_offer(
            content=text,
            company=company_hint,
            official_domain=off_domain,
            recruiter_email=rec_email,
            research_consent=req.research_consent,
            ai_consent=req.ai_consent,
        )
        tools_run.append(job_result)
        report_dict = job_result["report"]
        session.active_report = report_dict

        # If recruiter email provided, also run recruiter signal tool
        if rec_email and off_domain:
            rec_result = await tool_check_recruiter_signals(rec_email, off_domain)
            tools_run.append(rec_result)
            findings.extend(rec_result.get("findings", []))

        # Red flags and evidence
        flags = job_result.get("red_flags", [])
        score = job_result.get("risk_score", 0)
        level = job_result.get("risk_level", "Insufficient Evidence")
        risk_assessment = {
            "level": level,
            "score": score,
            "reasons": [f["label"] for f in flags]
        }
        evidence_sources = report_dict.get("sources", [])
        suggested_steps = report_dict.get("recommendations", [])

        # Build natural conversational explanation
        flag_bullets = "\n".join(f"• **{f['label']}**: {f['explanation']}" for f in flags)
        assistant_text = (
            f"I completed an investigation of your submitted communication.\n\n"
            f"**Assessment**: **{level} Concern** (Heuristic Score: {score}/100)\n\n"
            f"**Key Findings**:\n{flag_bullets if flags else '• No immediate high-risk keyword signals detected in initial rules screening.'}\n\n"
            f"**Recommended Actions**:\n"
            + "\n".join(f"1. {r}" for r in suggested_steps[:3]) + "\n\n"
            f"**Uncertainty Note**: {report_dict.get('limitations', ['Verification requires independent confirmation.'])[0]}"
        )

        # A provider is optional and receives only the structured report (never
        # the raw submitted message). Use it only after explicit consent and
        # only when its validated, grounded response is available.
        ai_explanation = report_dict.get("ai_explanation")
        if ai_explanation:
            assistant_text = (
                f"{ai_explanation.get('answer', assistant_text)}\n\n"
                f"**Assessment**: **{level} Concern** (Heuristic Score: {score}/100)\n\n"
                f"**Safety steps**:\n" + "\n".join(f"• {r}" for r in suggested_steps[:3]) + "\n\n"
                f"**Uncertainty Note**: {ai_explanation.get('uncertainty', uncertainty)}"
            )
            uncertainty = ai_explanation.get("uncertainty", uncertainty)

    suggested_prompts = [
        "Explain why this offer is risky.",
        "What specific steps should I take next?",
        "Can you verify the recruiter's domain?",
        "Ask ScamShield about this report."
    ]

    chat_turn = MessageItem(
        role="assistant",
        content=assistant_text,
        tools_executed=tools_run,
        risk_level=risk_assessment.get("level") if risk_assessment else None,
        risk_score=risk_assessment.get("score") if risk_assessment else None,
        findings=findings,
        evidence_leads=evidence_sources,
        uncertainty=uncertainty,
        suggested_prompts=suggested_prompts
    )
    session.messages.append(chat_turn)

    return ChatResponse(
        session_id=session.session_id,
        assistant_message=assistant_text,
        tools_executed=tools_run,
        findings=findings,
        evidence_sources=evidence_sources,
        risk_assessment=risk_assessment,
        uncertainty=uncertainty,
        suggested_next_steps=suggested_steps,
        suggested_prompts=suggested_prompts,
        report=report_dict,
        mode=("AI-assisted Guardian (grounded report explanation)"
              if report_dict and report_dict.get("ai_explanation")
              else "Local Rules-based Guardian Mode")
    )
