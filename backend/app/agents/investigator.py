import asyncio
from app.schemas.core import Report
from app.services.search import search_service, SearchError
from app.services.risk import analyze_rules
from app.services.llm import explain
from app.security.validation import domain, public_term
from app.database.store import new_id, now

async def investigate(request, search=None):
    search=search or search_service
    flags,facts,extracted,quality=analyze_rules(request)
    workflow=[{'agent':'Intake','status':'complete','detail':f'Validated {request.kind}; extracted local indicators.'}]
    sources=[]
    errors=[]
    queries=[]
    official=domain(request.official_domain) if request.official_domain else ''
    target=public_term(request.company) or (domain(extracted['urls'][0]) if extracted['urls'] else '')
    if not request.research_consent:
        status='not_requested'
        errors.append('External research is disabled. Only local rules were run.')
    elif not target:
        status='insufficient_input'
        errors.append('Add a company name or public URL to research without sharing your full message.')
    else:
        queries=[f'"{target}" official careers recruitment',f'"{target}" scam warning recruitment fees']
        if official:
            queries[0]=f'site:{official} careers recruitment fees'
        status='complete'
        async def research():
            nonlocal status
            for query in queries:
                try:
                    found=await search.web(query,official)
                    known={x.url for x in sources}
                    sources.extend(s for s in found if s.url not in known)
                except SearchError as exc:
                    errors.append(str(exc))
                    status='partial' if sources else 'failed'
                    break
            # An adaptive third query resolves an observed fee-policy tension.
            has_fee=any(f.code=='upfront_fee' for f in flags)
            if has_fee and any('fee' in s.snippet.lower() for s in sources) and status=='complete':
                query=f'"{target}" recruitment "no fees"'
                queries.append(query)
                try:
                    found=await search.web(query,official)
                    known={x.url for x in sources}
                    sources.extend(s for s in found if s.url not in known)
                except SearchError as exc:
                    errors.append(str(exc));status='partial'
        try:
            await asyncio.wait_for(research(),timeout=90)
        except asyncio.TimeoutError:
            errors.append('Research exceeded the 90-second total budget.')
            status='partial' if sources else 'failed'
        if not sources and status=='complete':
            status='empty'
    # Dedupe conservatively, then assign stable report-local citation IDs.
    sources=list({s.url:s for s in sources}.values())[:24]
    support=[];contradictions=[]
    for i,s in enumerate(sources,1):
        s.id=f'S{i}'
        snippet=s.snippet.lower()
        if any(f.code=='upfront_fee' for f in flags) and any(phrase in snippet for phrase in ['no fees','never charge','does not charge','no recruitment fee']):
            s.stance='Potential contradiction; check source and applicability'
            contradictions.append(f'[{s.id}] Search excerpt describes a no-fee policy while the submitted text mentions payment. Confirm company, role and context on the source.')
        elif any(term in snippet for term in ['scam','fraud','warning']):
            s.stance='Warning language; relevance unconfirmed'
            support.append(f'[{s.id}] Warning-related language appears in a search excerpt. This does not establish that this offer is fraudulent.')
    score=min(100,sum(f.points for f in flags))
    level='High' if score>=60 else 'Medium' if score>=25 else 'Insufficient Evidence'
    # No low-risk assurance from absence of indicators or snippets alone.
    confidence='Limited' if sources else 'Unavailable'
    unverified=['Company legitimacy, recruiter identity and the authenticity of this specific offer remain unverified.',
        'Search snippets are leads, not a complete review of the underlying pages.']
    if extracted['deadline']!='Not stated':
        unverified.append('The advertised deadline has not been independently confirmed.')
    if not sources:
        unverified.append('No public evidence was obtained. Missing results do not prove fraud.')
    workflow.extend([
        {'agent':'Research planner','status':'complete','detail':f'{len(queries)} bounded queries; only company/domain terms are sent.'},
        {'agent':'Research','status':status,'detail':f'{len(sources)} search excerpts collected.'},
        {'agent':'Verification','status':'limited','detail':'Compared source hosts and fee-policy language; ownership and identity remain unverified.'},
        {'agent':'Risk analysis','status':'complete','detail':f'{len(flags)} local heuristic indicators; weights are visible.'},
        {'agent':'Recommendation','status':'complete','detail':'Safety steps generated from observed indicators.'},
        {'agent':'Report','status':'complete','detail':'Structured report generated; not saved unless requested.'}])
    recommendations=['Find the organization’s official contact channel independently and confirm this exact offer.',
        'Do not share passwords, OTPs or banking credentials with a recruiter.',
        'Review original evidence links carefully; do not treat a search ranking or HTTPS as proof of legitimacy.']
    if any(f.code=='upfront_fee' for f in flags):
        recommendations.insert(0,'Pause any payment until you have independently confirmed the purpose, recipient and refund terms.')
    if any(f.code=='penalty' for f in flags):
        recommendations.append('Ask for the exact contract terms in writing and seek qualified advice for binding obligations.')
    report=Report(report_id=new_id(),analysis_type=request.kind,created_at=now(),risk_score=score,risk_level=level,
        evidence_confidence=confidence,research_status=status,research_errors=errors,red_flags=flags,verified_facts=facts,
        unverified_claims=unverified,supporting_evidence=support,contradictory_evidence=contradictions,sources=sources,
        recommendations=recommendations,extracted=extracted,quality=quality,workflow=workflow,
        summary=f'{len(flags)} potential risk indicator(s) found. The rule score is {score}/100; it is not a fraud probability. Independent verification is still required.',
        limitations=['Heuristic screening can miss scams and flag legitimate messages. Negation handling is limited.',
            'No destination pages were fetched. DNS, redirects, malware, email authentication and identity were not verified.',
            'No independently authenticated evidence is available to justify a Low risk classification.',
            'Opportunity quality is description completeness; resume relevance is a separate keyword measure.'])
    if request.ai_consent:
        report.ai_explanation,report.ai_status=await explain(report)
    return report
