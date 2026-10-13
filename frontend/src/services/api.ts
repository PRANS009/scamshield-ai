let token=localStorage.getItem('scamshield-workspace');
if(!token){token=crypto.randomUUID();localStorage.setItem('scamshield-workspace',token);}
export async function api<T=any>(path:string,body?:unknown,method?:string):Promise<T>{
  const isForm=body instanceof FormData;
  const response=await fetch('/api/v1'+path,{method:method||(body?'POST':'GET'),headers:{'X-Workspace-Token':token!,...(!isForm&&body?{'Content-Type':'application/json'}:{})},body:body?(isForm?body:JSON.stringify(body)):undefined});
  if(!response.ok){const error=await response.json().catch(()=>({detail:'Server unavailable'}));throw new Error(typeof error.detail==='string'?error.detail:JSON.stringify(error.detail));}
  if(response.status===204)return undefined as T;
  return response.json();
}
export async function downloadReport(report:unknown){
  const response=await fetch('/api/v1/reports/pdf',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(report)});
  if(!response.ok)throw new Error('PDF generation failed. Please retry.');
  const url=URL.createObjectURL(await response.blob());const a=document.createElement('a');a.href=url;a.download='scamshield-report.pdf';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function safeHref(value:string):string|undefined {try{const u=new URL(value);return ['https:','http:'].includes(u.protocol)?u.href:undefined;}catch{return undefined;}}
