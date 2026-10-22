import hashlib
import json
import re
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from difflib import unified_diff
from uuid import UUID
from fastapi import FastAPI, HTTPException, Request, Header, Depends, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.concurrency import run_in_threadpool
from pathlib import Path
from sqlalchemy import select,delete
from app import config
from app.database.store import init_db,Session,SavedReport,EvidenceRecord,Application,Snapshot,now,new_id
from app.schemas.core import Investigation,Report,Followup,MatchInput,CareerInput,ApplicationInput,SnapshotInput
from app.agents.investigator import investigate
from app.services.search import search_service,SearchError
from app.services.llm import explain
from app.services.career import match,roadmap,market
from app.services.files import read_upload,extract_document,decode_qr,make_pdf
from app.security.validation import redact,normalize_url,redact_payload

@asynccontextmanager
async def lifespan(app):
    init_db()
    yield

app=FastAPI(title='ScamShield AI',version='1.0.0',lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=config.CORS_ORIGINS,allow_credentials=False,allow_methods=['GET','POST','PUT','DELETE'],allow_headers=['Content-Type','X-Workspace-Token'])
visits=defaultdict(deque)

@app.middleware('http')
async def limits(request:Request,call_next):
    if request.url.path.startswith('/api/'):
        length=request.headers.get('content-length','0')
        if not length.isdigit() or int(length)>config.MAX_UPLOAD+100_000:
            return JSONResponse({'detail':'Request body is too large.'},status_code=413)
        ip=request.client.host if request.client else 'local'
        tick=time.monotonic()
        if len(visits)>2000:
            for key in list(visits):
                if not visits[key] or tick-visits[key][-1]>60:
                    del visits[key]
        window=visits[ip]
        while window and tick-window[0]>60:
            window.popleft()
        if len(window)>=60:
            return JSONResponse({'detail':'Rate limit: wait one minute before retrying.'},status_code=429,headers={'Retry-After':'60'})
        window.append(tick)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['Referrer-Policy']='no-referrer'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Cache-Control']='no-store'
    return response

@app.exception_handler(RequestValidationError)
async def validation_error(request,exc):
    # Do not echo private input or file bytes from Pydantic errors.
    return JSONResponse({'detail':[{'loc':e['loc'],'msg':e['msg']} for e in exc.errors()]},status_code=422)

@app.exception_handler(SearchError)
async def search_error(request,exc):
    return JSONResponse({'detail':str(exc)},status_code=503)

@app.exception_handler(ValueError)
async def value_error(request,exc):
    return JSONResponse({'detail':str(exc)},status_code=422)

def owner(x_workspace_token:str=Header(default='')):
    try:
        UUID(x_workspace_token)
    except ValueError:
        raise HTTPException(401,'A valid local workspace token is required for saved data.') from None
    return hashlib.sha256(x_workspace_token.encode()).hexdigest()

@app.api_route('/api/v1/health',methods=['GET','HEAD'])
def health():
    return {'status':'ok','version':'1.0.0','serpapi_configured':bool(config.SERPAPI_KEY),'llm_configured':bool(config.LLM_KEY and config.LLM_MODEL),
        'mode':'live integrations when configured; local heuristics otherwise'}

@app.post('/api/v1/agent/investigate',response_model=Report)
async def agent(body:Investigation):
    return await investigate(body)

def scan_handler(kind):
    async def handler(body:Investigation):
        return await investigate(body.model_copy(update={'kind':kind}))
    return handler
for path,kind in [('scans/url','url'),('scans/message','message'),('scans/email','email'),('scans/shopping','shopping'),('internships/analyze','internship'),('jobs/analyze','job')]:
    app.add_api_route('/api/v1/'+path,scan_handler(kind),methods=['POST'],response_model=Report,name=path.replace('/','_'))

@app.post('/api/v1/documents/extract')
async def document(file:UploadFile=File(...)):
    name,data=await read_upload(file,('.pdf','.txt'))
    text=await run_in_threadpool(extract_document,name,data)
    return {'text':text,'characters':len(text),'notice':'Extracted locally. No raw file was stored or sent to a model. Review before analysis.'}

@app.post('/api/v1/scans/qr')
async def qr(file:UploadFile=File(...)):
    _,data=await read_upload(file,('.png','.jpg','.jpeg'))
    content=await run_in_threadpool(decode_qr,data)
    is_url=content.lower().startswith(('http://','https://'))
    payment=content.lower().startswith('upi://')
    return {'content':content,'type':'URL' if is_url else 'Payment instruction' if payment else 'Text',
        'notice':'Decoded only; destination was not opened. Review the payee and amount independently. A QR code does not establish who receives money.'}

@app.get('/api/v1/jobs/search')
async def jobs(role:str=Query(min_length=2,max_length=120),location:str=Query(default='India',max_length=120),
               skills:str=Query(default='',max_length=200),preference:str=Query(default='',max_length=60),salary:str=Query(default='',max_length=60)):
    result=await search_service.jobs(role,location,skills,preference,salary)
    result['market']=market(result['jobs'])
    return result

@app.post('/api/v1/resume/match')
def resume_match(body:MatchInput):
    return match(body.resume,body.job_description)

@app.post('/api/v1/career/roadmap')
def career(body:CareerInput):
    return roadmap(body.skills,body.role,body.job_description)

@app.post('/api/v1/reports/pdf')
async def pdf(body:Report):
    return Response(await run_in_threadpool(make_pdf,body),media_type='application/pdf',headers={'Content-Disposition':'attachment; filename="scamshield-report.pdf"'})

@app.post('/api/v1/reports',status_code=201)
def save(body:Report,user=Depends(owner)):
    # Persist only explicitly saved, redacted report data, never original uploads.
    payload=json.dumps(redact_payload(body.model_dump()))
    with Session() as db:
        record=db.get(SavedReport,body.report_id)
        if record and record.owner!=user:
            raise HTTPException(404,'Report not found.')
        if record:
            return {'id':record.id,'saved':True}
        record=SavedReport(id=body.report_id,owner=user,created_at=now(),payload=payload)
        db.add(record)
        for source in body.sources:
            db.add(EvidenceRecord(id=new_id(),report_id=record.id,payload=json.dumps(redact_payload(source.model_dump()))))
        db.commit()
    return {'id':body.report_id,'saved':True}

@app.get('/api/v1/reports')
def reports(user=Depends(owner)):
    with Session() as db:
        records=db.scalars(select(SavedReport).where(SavedReport.owner==user).order_by(SavedReport.created_at.desc())).all()
        return [json.loads(r.payload) for r in records]

def get_saved(report_id,user):
    with Session() as db:
        record=db.get(SavedReport,report_id)
        if not record or record.owner!=user:
            raise HTTPException(404,'Report not found.')
        return Report.model_validate_json(record.payload)

@app.get('/api/v1/reports/{report_id}',response_model=Report)
def get_report(report_id:str,user=Depends(owner)):
    return get_saved(report_id,user)

@app.get('/api/v1/reports/{report_id}/pdf')
async def saved_pdf(report_id:str,user=Depends(owner)):
    return await pdf(get_saved(report_id,user))

@app.delete('/api/v1/reports/{report_id}',status_code=204)
def delete_report(report_id:str,user=Depends(owner)):
    get_saved(report_id,user)
    with Session() as db:
        db.execute(delete(EvidenceRecord).where(EvidenceRecord.report_id==report_id))
        db.execute(delete(SavedReport).where(SavedReport.id==report_id,SavedReport.owner==user));db.commit()

@app.post('/api/v1/assistant')
async def assistant(body:Followup):
    if body.ai_consent:
        answer,status=await explain(body.report,body.question)
        if answer:
            return {**answer,'mode':status}
    q=body.question.lower()
    report=body.report
    if 'score' in q or 'risk' in q:
        answer=report.summary+' '+' '.join(f'{f.label}: +{f.points}.' for f in report.red_flags)
    elif 'source' in q or 'evidence' in q:
        answer=f'{len(report.sources)} search excerpts were collected. '+' '.join(report.unverified_claims)
    else:
        answer=' '.join(report.recommendations)
    return {'answer':answer,'source_ids':[],'uncertainty':'This is a deterministic explanation of the supplied report. No new investigation was performed.',
        'mode':'Local explanation (LLM unavailable or not requested)'}

@app.post('/api/v1/incident-summary')
def incident(body:Report):
    return {'summary':'Potential incident summary — review and edit before any submission.\n'+body.summary+'\nObserved indicators:\n'+
        '\n'.join(f'- {f.label}: {f.explanation}' for f in body.red_flags)+'\nSource leads:\n'+
        '\n'.join(f'[{s.id}] {s.title}: {s.url}' for s in body.sources),
        'reporting_url':'https://cybercrime.gov.in/',
        'notice':'No complaint has been submitted. Preserve original messages, receipts and dates separately; this summary is not proof of fraud.'}

@app.get('/api/v1/applications')
def applications(user=Depends(owner)):
    with Session() as db:
        return [{'id':r.id,'created_at':r.created_at,**json.loads(r.payload)} for r in db.scalars(select(Application).where(Application.owner==user).order_by(Application.created_at.desc())).all()]

@app.post('/api/v1/applications',status_code=201)
def create_application(body:ApplicationInput,user=Depends(owner)):
    identifier=new_id()
    with Session() as db:
        db.add(Application(id=identifier,owner=user,created_at=now(),payload=json.dumps(redact_payload(body.model_dump()))));db.commit()
    return {'id':identifier,**body.model_dump()}

def owned_application(db,identifier,user):
    item=db.get(Application,identifier)
    if not item or item.owner!=user:
        raise HTTPException(404,'Application not found.')
    return item

@app.put('/api/v1/applications/{identifier}')
def update_application(identifier:str,body:ApplicationInput,user=Depends(owner)):
    with Session() as db:
        item=owned_application(db,identifier,user);item.payload=json.dumps(redact_payload(body.model_dump()));db.commit()
    return {'id':identifier,**body.model_dump()}

@app.delete('/api/v1/applications/{identifier}',status_code=204)
def delete_application(identifier:str,user=Depends(owner)):
    with Session() as db:
        item=owned_application(db,identifier,user)
        db.execute(delete(Snapshot).where(Snapshot.application_id==identifier));db.delete(item);db.commit()

@app.get('/api/v1/applications/{identifier}/snapshots')
def snapshots(identifier:str,user=Depends(owner)):
    with Session() as db:
        owned_application(db,identifier,user)
        rows=db.scalars(select(Snapshot).where(Snapshot.application_id==identifier).order_by(Snapshot.created_at)).all()
        diff=list(unified_diff(rows[-2].text.splitlines(),rows[-1].text.splitlines(),fromfile='Previous snapshot',tofile='Current snapshot',lineterm='')) if len(rows)>1 else []
        return {'snapshots':[{'id':r.id,'created_at':r.created_at,'text':r.text} for r in rows],'diff':diff,
            'notice':'Manual text snapshots only. Differences are observed text changes, not independently confirmed opportunity changes.'}

@app.post('/api/v1/applications/{identifier}/snapshots',status_code=201)
def snapshot(identifier:str,body:SnapshotInput,user=Depends(owner)):
    with Session() as db:
        owned_application(db,identifier,user)
        item=Snapshot(id=new_id(),application_id=identifier,created_at=now(),text=redact(body.text));db.add(item);db.commit()
    return snapshots(identifier,user)

@app.delete('/api/v1/workspace',status_code=204)
def erase(user=Depends(owner)):
    with Session() as db:
        report_ids=select(SavedReport.id).where(SavedReport.owner==user)
        app_ids=select(Application.id).where(Application.owner==user)
        db.execute(delete(EvidenceRecord).where(EvidenceRecord.report_id.in_(report_ids)))
        db.execute(delete(Snapshot).where(Snapshot.application_id.in_(app_ids)))
        db.execute(delete(SavedReport).where(SavedReport.owner==user))
        db.execute(delete(Application).where(Application.owner==user));db.commit()

# Optional production bundle: same-origin UI and API. API routes are registered first.
dist=Path(__file__).resolve().parents[2]/'frontend'/'dist'
if dist.exists():
    app.mount('/assets',StaticFiles(directory=dist/'assets'),name='assets')
    @app.api_route('/{path:path}',methods=['GET','HEAD'],include_in_schema=False)
    def spa(path:str):
        if path.startswith('api/'):
            raise HTTPException(404,'API route not found.')
        return FileResponse(dist/'index.html')
