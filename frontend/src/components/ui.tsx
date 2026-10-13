import {LoaderCircle,ArrowUpRight} from 'lucide-react';
import type {ReactNode} from 'react';
import {safeHref} from '../services/api';
export const PageTitle=({eyebrow,title,children}:{eyebrow:string;title:string;children?:ReactNode})=><header className="page-title"><span className="eyebrow">{eyebrow}</span><h1>{title}</h1>{children&&<p>{children}</p>}</header>;
export const ErrorBox=({error}:{error:string})=>error?<div className="alert error" role="alert">{error}</div>:null;
export const Busy=({text='Working…'}:{text?:string})=><span className="busy" role="status"><LoaderCircle size={17} className="spin"/>{text}</span>;
export const SourceLink=({url,children}:{url:string;children:ReactNode})=>safeHref(url)?<a href={safeHref(url)} target="_blank" rel="noopener noreferrer" className="source-link">{children}<ArrowUpRight size={14}/></a>:<span>{children} (link unavailable)</span>;
export const List=({items}:{items:string[]})=><ul className="text-list">{items.map((item,i)=><li key={i}>{item}</li>)}</ul>;
