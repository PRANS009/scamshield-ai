"""ScamShield AI 2.0 - Core Investigation Tools

Exposes real, validated security and research tools for the AI Guardian agent.
Each tool validates inputs, invokes real detection logic, and returns structured outputs.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from app.schemas.core import Investigation, Report, Source, Flag
from app.services.risk import analyze_rules, RULES, BRANDS
from app.agents.investigator import investigate
from app.services.search import search_service, SearchError
from app.security.validation import normalize_url, domain, redact

def get_tool_definitions() -> List[Dict[str, Any]]:
    """Returns tool specifications for documentation, capabilities API, and LLM function calling."""
    return [
        {
            "name": "analyze_message",
            "description": "Inspects suspicious text messages, SMS, WhatsApp chats, or emails for upfront payment demands, OTP/credential theft, artificial urgency, and scam patterns.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The exact message text to inspect."},
                    "sender_hint": {"type": "string", "description": "Optional sender name or number hint."}
                },
                "required": ["text"]
            }
        },
        {
            "name": "analyze_url",
            "description": "Validates, sanitizes, and evaluates a web link for lookalike brands, Punycode tricks, unencrypted HTTP, and suspicious domain patterns without opening the destination.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "The web URL to inspect."}
                },
                "required": ["url"]
            }
        },
        {
            "name": "investigate_job_offer",
            "description": "Performs an end-to-end multi-agent investigation of an internship or job offer, evaluating fees, contracts, recruiter domains, and description completeness.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "The job description, offer letter text, or communication."},
                    "company": {"type": "string", "description": "Company or organization name."},
                    "official_domain": {"type": "string", "description": "Known official domain of the employer."},
                    "recruiter_email": {"type": "string", "description": "Email address of the recruiter."},
                    "research_consent": {"type": "boolean", "description": "Whether public search research is authorized."}
                },
                "required": ["content"]
            }
        },
        {
            "name": "check_recruiter_signals",
            "description": "Compares recruiter contact domains against claimed company domains to detect impersonation or free/public mailbox use.",
            "parameters": {
                "type": "object",
                "properties": {
                    "recruiter_email": {"type": "string", "description": "Recruiter email address to verify."},
                    "official_domain": {"type": "string", "description": "Official company domain reference."}
                },
                "required": ["recruiter_email", "official_domain"]
            }
        },
        {
            "name": "search_public_evidence",
            "description": "Executes controlled, bounded public queries through SerpApi to retrieve known warnings, official career portals, and recruitment fee policies.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Company or domain keyword."},
                    "official_domain": {"type": "string", "description": "Official domain to restrict search context."}
                },
                "required": ["target"]
            }
        },
        {
            "name": "generate_safety_report",
            "description": "Compiles all observed red flags, source leads, unverified claims, and recommended safety steps into a standardized ScamShield safety report.",
            "parameters": {
                "type": "object",
                "properties": {
                    "investigation_kind": {"type": "string", "enum": ["message", "url", "internship", "job", "email", "qr"]},
                    "content": {"type": "string"}
                },
                "required": ["investigation_kind", "content"]
            }
        }
    ]


async def tool_analyze_message(text: str, sender_hint: str = "") -> Dict[str, Any]:
    """Analyzes message content for heuristic risk signals."""
    if not text or len(text.strip()) < 3:
        return {"error": "Message content must be at least 3 characters."}
    inv = Investigation(kind="message", content=text)
    flags, facts, extracted, _ = analyze_rules(inv)
    score = min(100, sum(f.points for f in flags))
    level = "High" if score >= 60 else "Moderate" if score >= 25 else "Low" if (flags and score < 25) else "Insufficient Evidence"
    return {
        "tool": "analyze_message",
        "status": "success",
        "red_flags": [f.model_dump() for f in flags],
        "risk_score": score,
        "risk_level": level,
        "extracted": extracted,
        "summary": f"Identified {len(flags)} risk indicator(s). Heuristic score: {score}/100."
    }


async def tool_analyze_url(url: str) -> Dict[str, Any]:
    """Inspects a URL safely without fetching the destination."""
    if not url or len(url.strip()) < 3:
        return {"error": "A valid URL string is required."}
    try:
        normalized = normalize_url(url.strip())
    except ValueError as e:
        return {
            "tool": "analyze_url",
            "status": "invalid_url",
            "error": str(e),
            "safety_note": "The URL failed safe normalization and was rejected to prevent SSRF or unsafe protocol access."
        }
    inv = Investigation(kind="url", content=normalized)
    flags, facts, extracted, _ = analyze_rules(inv)
    score = min(100, sum(f.points for f in flags))
    level = "High" if score >= 60 else "Moderate" if score >= 25 else "Low" if (flags and score < 25) else "Insufficient Evidence"
    return {
        "tool": "analyze_url",
        "status": "success",
        "normalized_url": normalized,
        "hostname": domain(normalized),
        "red_flags": [f.model_dump() for f in flags],
        "risk_score": score,
        "risk_level": level,
        "facts": facts,
        "limitations": "The destination page was not fetched. DNS records, server redirects, and page content were not examined."
    }


async def tool_investigate_job_offer(
    content: str,
    company: str = "",
    official_domain: str = "",
    recruiter_email: str = "",
    research_consent: bool = False,
    ai_consent: bool = False,
) -> Dict[str, Any]:
    """Runs a full investigation of an internship or job offer."""
    if not content or len(content.strip()) < 3:
        return {"error": "Offer content must be at least 3 characters."}
    inv = Investigation(
        kind="internship",
        content=content,
        company=company,
        official_domain=official_domain,
        recruiter_email=recruiter_email,
        research_consent=research_consent,
        ai_consent=ai_consent,
    )
    report = await investigate(inv)
    return {
        "tool": "investigate_job_offer",
        "status": "success",
        "report": report.model_dump(),
        "risk_score": report.risk_score,
        "risk_level": report.risk_level,
        "red_flags": [f.model_dump() for f in report.red_flags],
        "recommendations": report.recommendations,
        "unverified_claims": report.unverified_claims,
        "sources_count": len(report.sources)
    }


async def tool_check_recruiter_signals(recruiter_email: str, official_domain: str) -> Dict[str, Any]:
    """Evaluates recruiter email consistency with the employer's official domain."""
    email = recruiter_email.strip().lower()
    off = domain(official_domain) if official_domain else ""
    if "@" not in email:
        return {"error": "Invalid recruiter email address."}
    recruiter_dom = email.rsplit("@", 1)[-1]
    is_public_provider = recruiter_dom in ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "proton.me", "rediffmail.com"]
    mismatch = bool(off and recruiter_dom != off and not recruiter_dom.endswith("." + off))
    
    findings = []
    if is_public_provider:
        findings.append(f"Recruiter is using a free public mail provider (@{recruiter_dom}) rather than a corporate domain.")
    if mismatch:
        findings.append(f"Recruiter domain (@{recruiter_dom}) does not match the official organization domain (@{off}).")
    if not mismatch and not is_public_provider and off:
        findings.append(f"Domain matches official reference (@{off}), but email header authentication remains unverified.")

    return {
        "tool": "check_recruiter_signals",
        "status": "success",
        "recruiter_domain": recruiter_dom,
        "official_domain": off,
        "is_public_provider": is_public_provider,
        "mismatch": mismatch,
        "findings": findings
    }


async def tool_search_public_evidence(target: str, official_domain: str = "") -> Dict[str, Any]:
    """Retrieves external evidence safely via SerpApi."""
    if not target or len(target.strip()) < 2:
        return {"error": "Target keyword or company name is required."}
    try:
        sources = await search_service.web(f'"{target}" scam warning recruitment fees', official_domain)
        return {
            "tool": "search_public_evidence",
            "status": "success",
            "sources": [s.model_dump() for s in sources],
            "count": len(sources),
            "notice": "Search results are leads and snippets, not verified legal determinations."
        }
    except SearchError as e:
        return {
            "tool": "search_public_evidence",
            "status": "error",
            "error": str(e),
            "notice": "External search could not be completed; continuing with local analysis."
        }


async def tool_generate_safety_report(investigation_kind: str, content: str) -> Dict[str, Any]:
    """Generates and returns a complete Report object."""
    kind = investigation_kind if investigation_kind in ("url", "message", "email", "shopping", "internship", "job") else "message"
    inv = Investigation(kind=kind, content=content)
    report = await investigate(inv)
    return {
        "tool": "generate_safety_report",
        "status": "success",
        "report": report.model_dump()
    }
