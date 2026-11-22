import {useEffect,useState,type FormEvent} from 'react';
import {BookHeart,CheckCircle2,ChevronRight,LockKeyhole,MessageCircleHeart,NotebookPen,Plus,ShieldCheck,Trash2,UserRoundCheck,AlertTriangle,Send,LoaderCircle} from 'lucide-react';
import {DiaryAICompanion} from './DiaryAICompanion';
import './diary-workspace.css';

type Entry = {id:string;created_at:string;content:string};
type Contact = {id:number;contact_name:string;relationship:string;is_safe_to_contact:boolean};
type Pane = 'write'|'reflect';
const API='/api/senior';
async function request<T>(token:string,path:string,method='GET',body?:unknown):Promise<T>{
  const r=await fetch(API+path,{method,headers:{Authorization:`Bearer ${token}`,...(body?{'Content-Type':'application/json'}:{})},body:body?JSON.stringify(body):undefined});
  const json=await r.json().catch(()=>({}));
  if(!r.ok)throw new Error(typeof json.detail==='string'?json.detail:`Request failed (${r.status})`);
  return json as T;
}
function brief(content:string){const first=content.trim().split('\n').find(Boolean)||'Untitled reflection';return first.length>52?first.slice(0,52)+'…':first;}
export default function DiaryWorkspace({token}:{token:string}){
  const [entries,setEntries]=useState<Entry[]>([]);
  const [selected,setSelected]=useState<string|null>(null);
  const [pane,setPane]=useState<Pane>('write');
  const [draft,setDraft]=useState('');
  const [loading,setLoading]=useState(true);
  const [saving,setSaving]=useState(false);
  const [error,setError]=useState('');
  const [notice,setNotice]=useState('');
  const [supportOpen,setSupportOpen]=useState(false);
  const [contacts,setContacts]=useState<Contact[]>([]);
  const [contactName,setContactName]=useState('');
  const [contactRelation,setContactRelation]=useState('teacher');
  const [safeContact,setSafeContact]=useState(false);
  const [safetyCategory,setSafetyCategory]=useState('other_urgent');
  const [safetyContact,setSafetyContact]=useState('');
  const [supportBusy,setSupportBusy]=useState(false);
  const active=entries.find(e=>e.id===selected)||null;
  useEffect(()=>{
    let live=true;setLoading(true);
    request<Entry[]>(token,'/diary').then(data=>{if(live){setEntries(data);setSelected(old=>old&&data.some(e=>e.id===old)?old:(data[0]?.id??null));}})
      .catch(e=>{if(live)setError(e instanceof Error?e.message:String(e));})
      .finally(()=>{if(live)setLoading(false)});
    return ()=>{live=false};
  },[token]);
  useEffect(()=>{
    if(!supportOpen)return;
    let live=true;
    request<Contact[]>(token,'/trusted-contacts').then(c=>{if(live)setContacts(c)}).catch(()=>{});
    return ()=>{live=false};
  },[supportOpen,token]);
  function newEntry(){setSelected(null);setPane('write');setError('');setNotice('');}
  function openEntry(id:string){setSelected(id);setPane('write');setError('');setNotice('');}
  async function save(event:FormEvent){
    event.preventDefault();if(!draft.trim()||saving)return;
    setSaving(true);setError('');setNotice('');
    try{
      const created=await request<{id:string}>(token,'/diary','POST',{content:draft.trim()});
      const list=await request<Entry[]>(token,'/diary');
      setEntries(list);setSelected(created.id);setDraft('');setNotice('Your reflection was saved securely.');
    }catch(e){setError(e instanceof Error?e.message:String(e));}
    finally{setSaving(false)}
  }
  async function removeEntry(entry:Entry){
    if(!window.confirm('Delete this entry and its AI conversation permanently?'))return;
    setError('');setNotice('');
    try{
      await request(token,`/diary/${entry.id}`,'DELETE');
      const next=entries.filter(x=>x.id!==entry.id);
      setEntries(next);setSelected(next[0]?.id??null);setPane('write');setNotice('Entry deleted.');
    }catch(e){setError(e instanceof Error?e.message:String(e));}
  }
  async function addContact(event:FormEvent){
    event.preventDefault();setSupportBusy(true);setError('');
    try{
      await request(token,'/trusted-contacts','POST',{contact_name:contactName,relationship:contactRelation,safe_to_contact:safeContact});
      setContactName('');setSafeContact(false);
      setContacts(await request<Contact[]>(token,'/trusted-contacts'));
      setNotice('Trusted contact saved. This does not notify them.');
    }catch(e){setError(e instanceof Error?e.message:String(e));}
    finally{setSupportBusy(false)}
  }
  async function seekHelp(){
    setSupportBusy(true);setError('');
    try{
      const result=await request<{notice:string}>(token,'/request-human-help','POST',{category:safetyCategory,contact_id:safetyContact?Number(safetyContact):null});
      setNotice(result.notice||'Your request was recorded. This does not send a notification.');
    }catch(e){setError(e instanceof Error?e.message:String(e));}
    finally{setSupportBusy(false)}
  }
  return <section className="edj-workspace" aria-label="Private journal workspace">
    <header className="edj-bar">
      <div className="edj-heading"><span className="edj-mark"><BookHeart size={20}/></span><div><h2>Private journal</h2><span>Write privately. Reflect at your pace.</span></div></div>
      <div className="edj-bar-actions"><span className="edj-secure"><LockKeyhole size={14}/> Encrypted entries</span><button type="button" className="edj-help-button" onClick={()=>setSupportOpen(x=>!x)} aria-expanded={supportOpen}><ShieldCheck size={16}/> Support</button></div>
    </header>
    <div className="edj-columns">
      <aside className="edj-library" aria-label="Saved journal entries">
        <div className="edj-library-header"><strong>My entries</strong><span>{entries.length}</span></div>
        <button type="button" className="edj-new" onClick={newEntry}><Plus size={17}/> New reflection</button>
        <div className="edj-entries">
          {loading?<p className="edj-muted">Loading your private entries…</p>:entries.length===0?<p className="edj-muted">Your journal starts with one thought. Write whenever you feel ready.</p>:entries.map(e=><button type="button" key={e.id} className={`edj-entry ${selected===e.id?'is-selected':''}`} onClick={()=>openEntry(e.id)} aria-current={selected===e.id?'true':undefined}>
            <span className="edj-entry-date">{new Date(e.created_at).toLocaleDateString(undefined,{month:'short',day:'numeric',year:'numeric'})}</span><strong>{brief(e.content)}</strong><ChevronRight size={15}/>
          </button>)}
        </div>
        <div className="edj-library-foot"><LockKeyhole size={15}/> Only you can open your entries through your account.</div>
      </aside>
      <div className="edj-main">
        <div className="edj-tabs" role="tablist" aria-label="Journal mode">
          <button type="button" role="tab" aria-selected={pane==='write'} className={pane==='write'?'active':''} onClick={()=>setPane('write')}><NotebookPen size={17}/> {active?'Read entry':'Write'}</button>
          <button type="button" role="tab" aria-selected={pane==='reflect'} className={pane==='reflect'?'active':''} disabled={!active} onClick={()=>setPane('reflect')}><MessageCircleHeart size={17}/> Reflect with AI</button>
        </div>
        {pane==='write'?active?<div className="edj-entry-view" role="tabpanel">
          <div className="edj-entry-view-header"><div><span className="edj-kicker">SAVED REFLECTION</span><h3>{new Date(active.created_at).toLocaleDateString(undefined,{dateStyle:'long'})}</h3></div><button type="button" title="Delete this reflection and its AI conversation" className="edj-delete" onClick={()=>removeEntry(active)}><Trash2 size={17}/><span>Delete</span></button></div>
          <div className="edj-entry-content">{active.content}</div>
          <div className="edj-entry-footer"><span><CheckCircle2 size={16}/> Saved privately</span><button type="button" className="edj-primary" onClick={()=>setPane('reflect')}><MessageCircleHeart size={17}/> Reflect with AI <ChevronRight size={16}/></button></div>
        </div>:<form className="edj-editor" onSubmit={save} role="tabpanel">
          <div className="edj-editor-title"><span className="edj-kicker">NEW REFLECTION</span><h3>What's on your mind?</h3><p>You can write about a good moment, a difficult feeling, or something you want to understand.</p></div>
          <textarea aria-label="Write your private journal entry" value={draft} onChange={e=>setDraft(e.target.value)} maxLength={10000} required placeholder="Today, I felt…"/>
          <div className="edj-editor-footer"><span>{draft.length.toLocaleString()} / 10,000</span><button className="edj-primary" type="submit" disabled={!draft.trim()||saving}>{saving?<LoaderCircle className="edj-spinner" size={17}/>:<LockKeyhole size={16}/>} Save reflection</button></div>
        </form>:<div className="edj-ai-shell" role="tabpanel">
          {active&&<div className="edj-ai-context"><div><span className="edj-kicker">REFLECTING ON</span><strong>{brief(active.content)}</strong></div><button type="button" onClick={()=>setPane('write')}>Read entry</button></div>}
          <DiaryAICompanion token={token} entries={entries} selectedEntryId={selected??''} embedded/>
        </div>}
      </div>
    </div>
    {(error||notice)&&<div className={`edj-toast ${error?'is-error':''}`} role={error?'alert':'status'}>{error||notice}<button type="button" aria-label="Dismiss message" onClick={()=>{setError('');setNotice('')}}>×</button></div>}
    {supportOpen&&<div className="edj-support-overlay" role="dialog" aria-modal="true" aria-label="Safety and trusted contacts">
      <div className="edj-support-panel"><div className="edj-support-head"><h3><UserRoundCheck size={20}/> Trusted people & safety</h3><button type="button" onClick={()=>setSupportOpen(false)} aria-label="Close support">×</button></div>
      <div className="edj-support-content"><p><AlertTriangle size={17}/> This journal is not monitored for emergencies. If you are in danger, contact a trusted adult or local emergency services directly.</p>
      <form className="edj-support-form" onSubmit={addContact}><h4>Add a trusted contact</h4><label>Name<input required minLength={2} maxLength={120} value={contactName} onChange={e=>setContactName(e.target.value)}/></label><label>Relationship<select value={contactRelation} onChange={e=>setContactRelation(e.target.value)}><option value="teacher">Teacher</option><option value="parent">Parent</option><option value="guardian">Guardian</option><option value="other">Other trusted adult</option></select></label><label className="edj-checkbox"><input type="checkbox" checked={safeContact} onChange={e=>setSafeContact(e.target.checked)}/> I believe this person is safe to contact</label><button disabled={supportBusy} type="submit">Save contact</button></form>
      <form className="edj-support-form" onSubmit={e=>{e.preventDefault();void seekHelp()}}><h4>Record a request for human help</h4><label>Reason<select value={safetyCategory} onChange={e=>setSafetyCategory(e.target.value)}><option value="other_urgent">Urgent support</option><option value="self_harm">Self-harm concerns</option><option value="violence">Violence</option><option value="abuse">Abuse</option></select></label><label>Safe contact<select value={safetyContact} onChange={e=>setSafetyContact(e.target.value)}><option value="">No contact selected</option>{contacts.filter(c=>c.is_safe_to_contact).map(c=><option key={c.id} value={c.id}>{c.contact_name} ({c.relationship})</option>)}</select></label><button disabled={supportBusy} type="submit"><Send size={16}/> Record request</button><small>Recording a request does not send a message or guarantee that someone will see it.</small></form></div></div>
    </div>}
  </section>;
}
