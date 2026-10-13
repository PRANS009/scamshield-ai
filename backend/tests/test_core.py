import io
from uuid import uuid4
import httpx,pytest
from app.schemas.core import Investigation
from app.security.validation import normalize_url
from app.services.search import SearchService,SearchError
from app.agents.investigator import investigate
from app.services.risk import analyze_rules
from app.services.career import match

@pytest.mark.parametrize('value',['http://127.0.0.1','http://10.1.2.3','https://169.254.169.254','http://localhost','http://a.local','http://2130706433','file:///etc/passwd','https://user:pass@example.com','https://example.com:8080','javascript:alert(1)','http://[::1]','https://a..com','https://bad_host.com'])
def test_unsafe_urls(value):
    with pytest.raises(ValueError):normalize_url(value)

def test_url_normalization():assert normalize_url('Example.COM/path#frag')=='https://example.com/path'

def test_message_risk(client):
    response=client.post('/api/v1/scans/message',json={'content':'Pay a registration fee immediately. Send your OTP now.'})
    assert response.status_code==200
    d=response.json();assert d['risk_score']>=60 and d['risk_level']=='High'
    assert d['research_status']=='not_requested' and not d['sources']

def test_negation():
    flags,*_=analyze_rules(Investigation(content='We never charge a registration fee. Do not share your OTP.'))
    assert not flags

def test_legitimate_looking_not_certified(client):
    d=client.post('/api/v1/internships/analyze',json={'content':'Role: Python Intern. Stipend: INR 10000. Duration: 3 months. Weekly mentorship; build APIs. 20 hours per week.'}).json()
    assert d['risk_score']==0 and d['risk_level']=='Insufficient Evidence' and d['quality']['score']>0

def test_mismatch():
    flags,*_=analyze_rules(Investigation(content='Software role and interview details',official_domain='example.com',recruiter_email='hiring@example-careers.com'))
    assert 'recruiter_mismatch' in [f.code for f in flags]

def test_missing_search_key(client):
    d=client.post('/api/v1/agent/investigate',json={'content':'Role: Python intern. Pay a registration fee.','company':'Example','research_consent':True}).json()
    assert d['research_status']=='failed' and 'SERPAPI_API_KEY' in d['research_errors'][0] and d['sources']==[]

@pytest.mark.asyncio
async def test_timeout():
    calls=[]
    async def handler(request):calls.append(request);raise httpx.ReadTimeout('timeout')
    s=SearchService(key='test-only',transport=httpx.MockTransport(handler))
    with pytest.raises(SearchError,match='timed out'):await s.web('query')
    assert len(calls)==2

@pytest.mark.asyncio
async def test_rate_limit():
    s=SearchService(key='test-only',transport=httpx.MockTransport(lambda r:httpx.Response(429)))
    with pytest.raises(SearchError,match='rate limit'):await s.web('query')

@pytest.mark.asyncio
async def test_empty_results():
    s=SearchService(key='test-only',transport=httpx.MockTransport(lambda r:httpx.Response(200,json={'organic_results':[]})))
    r=await investigate(Investigation(content='Example role',company='Example',research_consent=True),search=s)
    assert r.research_status=='empty' and r.risk_level=='Insufficient Evidence' and not r.sources

@pytest.mark.asyncio
async def test_contradiction_and_bounded_research():
    calls=[]
    def handler(request):
        calls.append(request)
        return httpx.Response(200,json={'organic_results':[{'title':'Example hiring','link':'https://example.com/careers','snippet':'Example does not charge fees. Recruitment has no fees.'},{'title':'bad','link':'javascript:alert(1)','snippet':'bad'}]})
    s=SearchService(key='test-only',transport=httpx.MockTransport(handler))
    r=await investigate(Investigation(content='Pay a registration fee.',company='Example',official_domain='example.com',research_consent=True),search=s)
    assert len(calls)==3 and len(r.sources)==1 and r.contradictory_evidence
    assert 'unverified' in r.sources[0].source_type and r.evidence_confidence=='Limited'

@pytest.mark.asyncio
async def test_job_normalization():
    payload={'jobs_results':[{'title':'Developer','company_name':'Example','description':'Python SQL','apply_options':[{'title':'Example','link':'https://example.com/jobs'}],'detected_extensions':{'posted_at':'2 days ago','salary':'INR 20000 per month'}}]}
    s=SearchService(key='test-only',transport=httpx.MockTransport(lambda r:httpx.Response(200,json=payload)))
    r=await s.jobs('Developer','India')
    assert r['sample_count']==1 and r['jobs'][0]['links'][0]['url']=='https://example.com/jobs'
    assert r['jobs'][0]['salary']=='INR 20000 per month'

@pytest.mark.asyncio
async def test_cache():
    calls=[]
    def handler(r):calls.append(r);return httpx.Response(200,json={'organic_results':[]})
    s=SearchService(key='test-only',transport=httpx.MockTransport(handler))
    await s.web('x');await s.web('x');assert len(calls)==1

def test_api_url_rejection(client):assert client.post('/api/v1/scans/url',json={'content':'http://127.0.0.1'}).status_code==422

def test_schema_validation(client):
    assert client.post('/api/v1/agent/investigate',json={'kind':'unknown','content':'x'}).status_code==422
    assert client.post('/api/v1/scans/message',json={'content':'   '}).status_code==422

def test_report_save_isolation_pdf_delete(client):
    a={'X-Workspace-Token':str(uuid4())};b={'X-Workspace-Token':str(uuid4())}
    r=client.post('/api/v1/scans/message',json={'content':'Pay a registration fee immediately.'}).json()
    assert client.get('/api/v1/reports',headers=a).json()==[]
    assert client.post('/api/v1/reports',json=r,headers=a).status_code==201
    assert len(client.get('/api/v1/reports',headers=a).json())==1
    saved=client.get('/api/v1/reports/'+r['report_id'],headers=a)
    assert saved.status_code==200 and saved.json()['created_at']==r['created_at']
    assert client.get('/api/v1/reports/'+r['report_id'],headers=b).status_code==404
    pdf=client.get('/api/v1/reports/'+r['report_id']+'/pdf',headers=a)
    assert pdf.status_code==200 and pdf.content.startswith(b'%PDF-')
    assert client.delete('/api/v1/reports/'+r['report_id'],headers=a).status_code==204
    assert client.get('/api/v1/reports',headers=a).json()==[]

def test_pdf_escape(client):
    d=client.post('/api/v1/scans/message',json={'content':'Pay a registration fee.'}).json();d['summary']='<script>not markup</script> & characters'
    r=client.post('/api/v1/reports/pdf',json=d);assert r.status_code==200 and r.content.startswith(b'%PDF')

def test_upload_type_and_signature(client):
    assert client.post('/api/v1/documents/extract',files={'file':('evil.exe',b'data')}).status_code==415
    assert client.post('/api/v1/documents/extract',files={'file':('fake.pdf',b'not pdf')}).status_code==415
    assert client.post('/api/v1/documents/extract',files={'file':('resume.txt',b'Python developer with SQL skills')}).json()['text'].startswith('Python')

def test_pdf_extraction(client):
    from reportlab.pdfgen import canvas
    out=io.BytesIO();c=canvas.Canvas(out);c.drawString(40,800,'Python developer with SQL and React experience');c.save()
    r=client.post('/api/v1/documents/extract',files={'file':('resume.pdf',out.getvalue(),'application/pdf')})
    assert r.status_code==200 and 'Python' in r.json()['text']

def test_oversize_upload(client):
    assert client.post('/api/v1/documents/extract',files={'file':('large.txt',b'a'*(5*1024*1024+1))}).status_code==413

def test_resume_matching(client):
    d=client.post('/api/v1/resume/match',json={'resume':'I build Python and SQL projects.','job_description':'Python SQL Docker experience required.'}).json()
    assert d['score']==67 and d['missing']==['docker']

def test_no_resume_keywords():assert match('A creative person.','Looking for creative people.')['score'] is None

def test_tracker_snapshots_owner_delete(client):
    a={'X-Workspace-Token':str(uuid4())};b={'X-Workspace-Token':str(uuid4())}
    item=client.post('/api/v1/applications',json={'title':'Python intern'},headers=a).json();p='/api/v1/applications/'+item['id']
    assert client.put(p,json={'title':'Python intern','status':'Interview'},headers=a).status_code==200
    assert client.post(p+'/snapshots',json={'text':'Stipend: 10000'},headers=a).status_code==201
    latest=client.post(p+'/snapshots',json={'text':'Stipend: 12000'},headers=a).json()
    assert latest['diff'] and len(latest['snapshots'])==2
    assert client.get(p+'/snapshots',headers=b).status_code==404
    assert client.delete('/api/v1/workspace',headers=a).status_code==204
    assert client.get('/api/v1/applications',headers=a).json()==[]

def test_no_owner_token(client):assert client.get('/api/v1/reports').status_code==401

def test_qr_invalid_image(client):assert client.post('/api/v1/scans/qr',files={'file':('qr.png',b'no image')}).status_code==422

def test_qr_real(client):
    import cv2
    q=cv2.QRCodeEncoder_create().encode('https://example.com/qr')
    q=cv2.copyMakeBorder(q,4,4,4,4,cv2.BORDER_CONSTANT,value=255);q=cv2.resize(q,(400,400),interpolation=cv2.INTER_NEAREST)
    _,data=cv2.imencode('.png',q)
    r=client.post('/api/v1/scans/qr',files={'file':('qr.png',data.tobytes(),'image/png')})
    assert r.status_code==200 and r.json()['content']=='https://example.com/qr'

def test_followup_local(client):
    r=client.post('/api/v1/scans/message',json={'content':'Share your OTP immediately.'}).json()
    d=client.post('/api/v1/assistant',json={'report':r,'question':'Why this score?'}).json()
    assert 'score' in d['answer'] and 'Local' in d['mode']

def test_rate_limiting(client):
    for _ in range(60):assert client.get('/api/v1/health').status_code==200
    assert client.get('/api/v1/health').status_code==429

@pytest.mark.asyncio
async def test_llm_json_and_grounding(monkeypatch):
    from app.services.llm import explain
    from app import config
    r=await investigate(Investigation(content='Share your OTP immediately.'))
    monkeypatch.setattr(config,'LLM_KEY','test-key');monkeypatch.setattr(config,'LLM_MODEL','test-model')
    real_client=httpx.AsyncClient
    payload={'choices':[{'message':{'content':'{"answer":"Do not share an OTP.","source_ids":[],"uncertainty":"No external evidence."}'}}]}
    transport=httpx.MockTransport(lambda req:httpx.Response(200,json=payload))
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:real_client(transport=transport,**kw))
    answer,status=await explain(r)
    assert answer['answer']=='Do not share an OTP.'
    payload['choices'][0]['message']['content']='{"answer":"Unsupported.","source_ids":["S99"],"uncertainty":"Unknown"}'
    answer,status=await explain(r)
    assert answer is None and 'rejected' in status
