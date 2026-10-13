import re
from urllib.parse import urlsplit
from difflib import SequenceMatcher
from app.security.validation import normalize_url, domain
from app.schemas.core import Flag

RULES = [
 ('upfront_fee',r'\b(?:pay|deposit|transfer|send)\b.{0,70}\b(?:fee|registration|security|money|rupees|inr|rs)\b|\b(?:registration|processing|joining|security)\s+(?:fee|deposit)\b',32,'Upfront payment language','Payment before verification is a risk indicator. Check the full context; legitimate paid training is distinct from employment.'),
 ('credentials',r'\b(?:share|send|provide|tell|enter)\b.{0,55}\b(?:otp|password|pin|cvv)\b',36,'Credential or OTP request','Requests to disclose credentials or transaction codes can expose your account.'),
 ('urgency',r'\b(?:immediately|urgent|within \d+ (?:minutes|hours)|last chance|act now|account.{0,15}(?:blocked|suspended))\b',12,'Urgency or pressure','Pressure can reduce time available for independent checks.'),
 ('guarantee',r'\b(?:guaranteed? (?:job|placement|selection|returns)|100% (?:placement|selection|guarantee))\b',15,'Guaranteed outcome claim','Absolute placement or return guarantees need independent supporting evidence.'),
 ('no_interview',r'\b(?:no interview|without (?:an? )?interview|selected without applying)\b',10,'Unusual selection process','Some roles use alternative assessments; verify the advertised process through company channels.'),
 ('remote_access',r'\b(?:install|download)\b.{0,60}\b(?:anydesk|teamviewer|remote access|apk)\b',20,'Remote access or external app request','An unexpected app installation request may expose your device.'),
 ('penalty',r'\b(?:penalty|bond|liquidated damages|non.refundable|original certificates)\b',12,'Restrictive contract term','Read the exact obligation, amount and exit conditions. This is an informational flag, not a legal conclusion.'),
 ('discount',r'\b(?:9[0-9]% off|free iphone|free laptop|lottery winner|won a prize)\b',15,'Extraordinary promotion','Check the promotion using the brand’s independently located channels.'),
]

# These are explicit reference domains, not evidence that any submitted offer is authentic.
BRANDS={'google':'google.com','microsoft':'microsoft.com','amazon':'amazon.com','flipkart':'flipkart.com','tcs':'tcs.com','infosys':'infosys.com'}

def analyze_rules(request):
    text=request.content
    flags=[]
    facts=[]
    def add(code,label,points,explanation):
        if code not in [f.code for f in flags]:
            flags.append(Flag(code=code,label=label,points=points,explanation=explanation))
    # Inspect sentences separately and suppress explicit negations; this remains a heuristic.
    sentences=re.split(r'[.!?\n]+',text.lower())
    for code,pattern,points,label,explanation in RULES:
        for sentence in sentences:
            if re.search(pattern,sentence) and not re.search(r'\b(?:never|do not|don.t|no need to|not required to|no (?:registration |processing )?fee|without (?:any )?fee)\b',sentence):
                add(code,label,points,explanation)
                break
    candidates=[text] if request.kind in ('url','shopping') else re.findall(r'https?://[^\s<>"\)]+',text)
    urls=[]
    blocked=[]
    for candidate in candidates[:15]:
        try:
            url=normalize_url(candidate.rstrip('.,;'))
        except ValueError:
            if request.kind in ('url','shopping'):
                raise
            blocked.append(candidate[:100])
            continue
        urls.append(url)
        host=domain(url)
        if urlsplit(url).scheme=='http':
            add('http','Unencrypted HTTP URL',8,'HTTP lacks transport encryption; HTTPS alone would not establish legitimacy.')
        if 'xn--' in host:
            add('punycode','Internationalized domain encoding',8,'Internationalized domains are legitimate in many cases, but can resemble other names.')
        if host.count('.')>=4 or host.count('-')>=3:
            add('domain_pattern','Complex domain pattern',6,'A long or fragmented hostname deserves closer inspection; this alone is not proof of fraud.')
        for brand,official in BRANDS.items():
            if brand in host and host!=official and not host.endswith('.'+official):
                # Regional brand domains may be legitimate; never call this confirmed impersonation.
                add('brand_domain','Brand name on a different domain',12,f'The hostname contains {brand} but differs from the built-in reference {official}. Regional domains may be legitimate; verify independently.')
        facts.append(f'Observed hostname: {host}. The destination was not opened.')
    if blocked:
        add('blocked_url','Unsupported or internal link in content',10,'An embedded URL failed public-address validation and was not opened or researched.')
    official=domain(request.official_domain) if request.official_domain else ''
    recruiter=request.recruiter_email.strip().lower()
    if not recruiter:
        matches=re.findall(r'[\w.+-]+@([\w.-]+\.[a-zA-Z]{2,})',text)
        recruiter_domain=matches[0].lower() if matches else ''
    else:
        recruiter_domain=recruiter.rsplit('@',1)[-1]
    affiliation='Unknown: independent confirmation is required.'
    if official and recruiter_domain:
        same=recruiter_domain==official or recruiter_domain.endswith('.'+official)
        affiliation='Domain matches the user-supplied reference; identity and mailbox control are unverified.' if same else 'Domain differs from the user-supplied reference; third-party agencies are possible.'
        if not same:
            add('recruiter_mismatch','Recruiter domain mismatch',18,affiliation)
            if SequenceMatcher(None,recruiter_domain,official).ratio()>.75:
                add('lookalike','Possible lookalike recruiter domain',10,'Similar spelling can be an impersonation indicator; it is not an identity verification result.')
    def extract(pattern):
        match=re.search(pattern,text,re.I)
        return match.group(1).strip()[:200] if match else 'Not stated'
    extracted={'company':request.company or 'Not supplied','urls':urls,'recruiter_domain':recruiter_domain or 'Not stated',
        'affiliation':affiliation,'stipend_or_salary':extract(r'(?:stipend|salary)\s*[:\-]?\s*([^\n.;]{2,100})'),
        'duration':extract(r'(?:duration)\s*[:\-]?\s*([^\n.;]{2,80})'),
        'deadline':extract(r'(?:deadline|apply by|last date)\s*[:\-]?\s*([^\n.;]{2,80})'),
        'role':extract(r'(?:role|position|job title)\s*[:\-]?\s*([^\n.;]{2,100})')}
    quality=None
    if request.kind in ('internship','contract','job'):
        criteria={label:bool(re.search(pattern,text,re.I)) for label,pattern in {
            'Mentorship described':r'mentor|supervisor|weekly feedback','Responsibilities described':r'responsibilit|duties|you will|build|develop',
            'Learning described':r'learn|training|workshop','Pay disclosed':r'stipend|salary|unpaid',
            'Duration described':r'duration|\d+\s*(?:weeks|months)','Hours described':r'\d+\s*hours|workload|part.time|full.time',
            'Company supplied':re.escape(request.company) if request.company else r'(?!)'}.items()}
        if request.company:
            criteria['Company supplied']=True
        quality={'score':round(100*sum(criteria.values())/len(criteria)),'criteria':criteria,
            'meaning':'Description completeness only; not verified opportunity quality or fraud risk.'}
    return flags,facts,extracted,quality
