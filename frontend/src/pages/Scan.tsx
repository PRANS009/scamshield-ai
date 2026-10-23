import {useState} from 'react';
import {useNavigate} from 'react-router-dom';
import {ArrowRight,FileUp,ScanLine} from 'lucide-react';
import {api} from '../services/api';
import {useTask} from '../hooks/useTask';
import {PageTitle,ErrorBox,Busy} from '../components/ui';
import type {Kind,Report} from '../types';
const names:Record<Kind,string>={url:'Scan a suspicious link',message:'Look beyond the message',email:'Inspect a suspicious email',shopping:'Check a shopping website',internship:'Verify your next opportunity',job:'Investigate a job offer',contract:'Understand an offer letter',qr:'Decode before you follow'};
const samples:Partial<Record<Kind,string>>={message:'FICTIONAL TEST: You won a prize! Act now. Share your OTP immediately to claim it.',internship:'FICTIONAL TEST — Acme Learning\nRole: Python Intern\nStipend: INR 12,000 per month\nDuration: 3 months\nPay a registration fee of INR 1,999 immediately. Guaranteed placement. No interview.',job:'FICTIONAL TEST — Role: Software Developer\nPay a processing fee of INR 2,000 within 2 hours. Guaranteed selection.',url:'http://amazon-career-offer.example.com',shopping:'http://flipkart-sale-offer.example.com',email:'FICTIONAL TEST\nFrom: hiring@acme-careers.example.com\nYour account will be suspended. Send your password immediately.'};
export default function Scan({kind,onReport}:{kind:Kind;onReport:(r:Report)=>void}){
 const [content,setContent]=useState('');const[company,setCompany]=useState('');const[official,setOfficial]=useState('');const[email,setEmail]=useState('');const[research,setResearch]=useState(false);const[ai,setAi]=useState(false);const[fileNote,setFileNote]=useState('');
 const task=useTask();const navigate=useNavigate();
 async function upload(file:File|undefined){if(!file)return;await task.run(async()=>{const form=new FormData();form.append('file',file);const result=await api(kind==='qr'?'/scans/qr':'/documents/extract',form);setContent(result.content||result.text);setFileNote(result.notice);});}
 async function submit(e:React.FormEvent){e.preventDefault();await task.run(async()=>{const report=await api<Report>('/agent/investigate',{kind:kind==='qr'&&/^https?:\/\//i.test(content)?'url':kind,content,company,official_domain:official,recruiter_email:email,research_consent:research,ai_consent:ai});onReport(report);navigate('/report');});}
 return <><PageTitle eyebrow={kind==='internship'?'InternshipShield AI':'Evidence-led screening'} title={names[kind]}>Get a clear breakdown of observed signals, public evidence and what still needs checking.</PageTitle><div className="scan-layout"><form className="panel" onSubmit={submit}><div className="section-heading"><h2>Start an investigation</h2><span className="pill">Private by default</span></div>
 {kind==='qr'||['internship','contract','job'].includes(kind)?<label className="upload"><FileUp size={20}/><span>{kind==='qr'?'Upload QR image · PNG or JPEG':'Extract an offer letter · PDF or TXT'}<small>Up to 5 MB. Files are processed locally by the backend.</small></span><input aria-label="Upload document" type="file" accept={kind==='qr'?'.png,.jpg,.jpeg':'.pdf,.txt'} onChange={e=>upload(e.target.files?.[0])} disabled={task.busy}/></label>:null}
 {fileNote&&<p className="notice">{fileNote}</p>}
 <label>{kind==='url'||kind==='shopping'?'Website URL':'Content to examine'}<textarea required minLength={3} maxLength={25000} rows={kind==='url'||kind==='shopping'?3:8} value={content} onChange={e=>setContent(e.target.value)} placeholder={kind==='url'?'https://example.com/offer':'Paste the message, offer details, email text or decoded QR content…'}/></label>
 {samples[kind]&&<button className="text-button" type="button" onClick={()=>{setContent(samples[kind]!);setResearch(false);setAi(false);}}>Load a fictional test input</button>}
 <div className="form-grid"><label>Company name <small>Optional · used for public search</small><input maxLength={120} value={company} onChange={e=>setCompany(e.target.value)} placeholder="e.g. company on the offer"/></label><label>Known official domain <small>Your reference, not automatically verified</small><input maxLength={253} value={official} onChange={e=>setOfficial(e.target.value)} placeholder="company.com"/></label></div>
 <label>Recruiter email <small>Optional · compared locally</small><input type="email" value={email} maxLength={254} onChange={e=>setEmail(e.target.value)} placeholder="recruiter@company.com"/></label>
 <div className="consent"><label><input type="checkbox" checked={research} onChange={e=>setResearch(e.target.checked)}/><span>Research with SerpApi<small>Send company/domain search terms to SerpApi and its search provider. Full messages and files are not sent.</small></span></label><label><input type="checkbox" checked={ai} onChange={e=>setAi(e.target.checked)}/><span>Add an AI explanation<small>Send redacted report indicators and search excerpts to the configured model provider. Raw documents are excluded.</small></span></label></div>
 <ErrorBox error={task.error}/>
 <div className="button-group-row">
   <button className="primary wide" disabled={task.busy}>{task.busy?<Busy text="Investigating · up to 95 seconds"/>:<>Investigate <ArrowRight size={17}/></>}</button>
   {content.trim() && (
     <button
       type="button"
       className="guardian-btn"
       disabled={task.busy}
       onClick={() => navigate('/guardian', { state: { initialQuery: content } })}
     >
       Investigate with AI Guardian →
     </button>
   )}
 </div>
</form>
 <aside><div className="panel guidance"><ScanLine size={30}/><h3>A signal is a starting point.</h3><p>Our checks surface indicators. They cannot certify a person, website or opportunity as safe.</p><ol><li>Inspect the content</li><li>Research public evidence</li><li>Compare claims and sources</li><li>Choose your next step</li></ol></div><div className="panel subtle"><h3>You stay in control</h3><p>No suspicious destination is opened automatically. Reports are saved only when you choose Save.</p><p className="muted">Do not paste passwords, OTPs or financial account details.</p></div></aside></div></>;
}
