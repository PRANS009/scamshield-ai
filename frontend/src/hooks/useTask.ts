import {useState} from 'react';
export function useTask(){
 const [busy,setBusy]=useState(false);const[error,setError]=useState('');
 async function run<T>(task:()=>Promise<T>):Promise<T|undefined>{setBusy(true);setError('');try{return await task();}catch(e){setError(e instanceof Error?e.message:'Something went wrong.');}finally{setBusy(false);}}
 return {busy,error,run};
}
