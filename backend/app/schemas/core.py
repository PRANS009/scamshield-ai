from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator
from app.security.validation import normalize_url

Kind = Literal['url','message','email','shopping','internship','job','contract','qr']

class Investigation(BaseModel):
    kind: Kind = 'message'
    content: str = Field(min_length=3, max_length=25000)
    company: str = Field(default='', max_length=120)
    official_domain: str = Field(default='', max_length=253)
    recruiter_email: str = Field(default='', max_length=254)
    research_consent: bool = False
    ai_consent: bool = False
    @field_validator('content')
    @classmethod
    def nonblank(cls, value):
        if len(value.strip()) < 3:
            raise ValueError('Enter at least three non-space characters.')
        return value.strip()
    @field_validator('official_domain')
    @classmethod
    def official(cls, value):
        return normalize_url(value) if value.strip() else ''
    @field_validator('recruiter_email')
    @classmethod
    def email(cls, value):
        import re
        if value and not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', value):
            raise ValueError('Enter a valid recruiter email.')
        return value

class Source(BaseModel):
    id: str
    title: str
    url: str
    snippet: str
    retrieved_at: str
    query: str
    source_type: str = 'Third-party search result'
    stance: str = 'Unreviewed'

class Flag(BaseModel):
    code: str
    label: str
    points: int
    explanation: str

class Report(BaseModel):
    report_id: str
    analysis_type: str
    created_at: str
    risk_score: int = Field(ge=0, le=100)
    risk_level: str
    evidence_confidence: str
    research_status: str
    research_errors: list[str] = []
    red_flags: list[Flag] = []
    verified_facts: list[str] = []
    unverified_claims: list[str] = []
    supporting_evidence: list[str] = []
    contradictory_evidence: list[str] = []
    sources: list[Source] = []
    recommendations: list[str] = []
    extracted: dict = {}
    quality: Optional[dict] = None
    workflow: list[dict] = []
    summary: str
    ai_status: str = 'Not requested'
    ai_explanation: Optional[dict] = None
    limitations: list[str] = []

class Followup(BaseModel):
    report: Report
    question: str = Field(min_length=3, max_length=1000)
    ai_consent: bool = False

class MatchInput(BaseModel):
    resume: str = Field(min_length=10, max_length=25000)
    job_description: str = Field(min_length=10, max_length=25000)

class CareerInput(BaseModel):
    skills: str = Field(default='', max_length=2000)
    role: str = Field(min_length=2, max_length=120)
    job_description: str = Field(default='', max_length=25000)

class ApplicationInput(BaseModel):
    title: str = Field(min_length=2,max_length=150)
    company: str = Field(default='',max_length=150)
    url: str = Field(default='',max_length=2048)
    status: Literal['Saved','Applied','Assessment','Interview','Offer','Rejected'] = 'Saved'
    notes: str = Field(default='',max_length=4000)
    deadline: str = Field(default='',max_length=30)
    @field_validator('url')
    @classmethod
    def check_url(cls,value):
        return normalize_url(value) if value else ''

class SnapshotInput(BaseModel):
    text: str = Field(min_length=3,max_length=25000)
