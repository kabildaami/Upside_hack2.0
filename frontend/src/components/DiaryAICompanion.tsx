import {useEffect,useRef,useState,type FormEvent} from 'react';
import {HeartHandshake,Send,LockKeyhole,LoaderCircle} from 'lucide-react';
import './diary-ai.css';

type DiaryEntry={id:string;created_at:string;content:string};
type Turn={id?:number;role:'student'|'assistant';body:string};

export function DiaryAICompanion({token,entries,selectedEntryId,embedded=false}:{token:string;entries:DiaryEntry[];selectedEntryId?:string;embedded?:boolean}){
  const [entryId,setEntryId]=useState('');
  const [turns,setTurns]=useState<Turn[]>([]);
  const [message,setMessage]=useState('');
  const [consent,setConsent]=useState(false);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState('');
  const generation=useRef(0);
  const bottom=useRef<HTMLDivElement>(null);

  useEffect(()=>{
    setEntryId(current=>selectedEntryId!==undefined ? selectedEntryId : (entries.some(e=>e.id===current)?current:(entries[0]?.id??'')));
  },[entries,selectedEntryId]);

  useEffect(()=>{
    const request=++generation.current;
    setTurns([]);setError('');setConsent(false);
    if(!entryId)return;
    fetch(`/api/senior/diary/${entryId}/ai`,{headers:{Authorization:`Bearer ${token}`}})
      .then(async r=>{const data=await r.json();if(!r.ok)throw new Error(data.detail||`History unavailable (${r.status})`);return data as Turn[];})
      .then(data=>{if(request===generation.current)setTurns(data);})
      .catch(e=>{if(request===generation.current)setError(String(e.message||e));});
  },[entryId,token]);

  useEffect(()=>bottom.current?.scrollIntoView({block:'nearest',behavior:'smooth'}),[turns]);

  async function send(event:FormEvent){
    event.preventDefault();const text=message.trim();
    if(!text||!entryId||!consent||busy)return;
    setBusy(true);setError('');setMessage('');
    const request=++generation.current;
    setTurns(t=>[...t,{role:'student',body:text},{role:'assistant',body:''}]);
    let answer='';let completed=false;
    try{
      const response=await fetch(`/api/senior/diary/${entryId}/ai/stream`,{
        method:'POST',headers:{Authorization:`Bearer ${token}`,'Content-Type':'application/json'},
        body:JSON.stringify({message:text,external_ai_consent:true})});
      if(!response.ok){const detail=await response.json().catch(()=>({}));throw new Error(detail.detail||`AI unavailable (${response.status})`);}
      if(!response.body)throw new Error('Streaming is not supported in this browser');
      const reader=response.body.getReader();const decoder=new TextDecoder();let buffer='';
      for(;;){const {value,done}=await reader.read();if(done)break;buffer+=decoder.decode(value,{stream:true});
        const lines=buffer.split('\n');buffer=lines.pop()??'';
        for(const line of lines){if(!line.trim())continue;const update=JSON.parse(line);
          if(update.type==='error')throw new Error(update.message||'AI response interrupted');
          if(update.type==='done')completed=true;
          if(update.type==='delta'&&typeof update.text==='string'){
            answer+=update.text;
            if(request===generation.current)setTurns(previous=>previous.map((turn,i)=>i===previous.length-1?{...turn,body:answer}:turn));
          }
        }
      }
      if(!completed)throw new Error('AI stream ended before it was saved');
    }catch(e){
      if(request===generation.current){setError(e instanceof Error?e.message:String(e));
        setTurns(previous=>previous.slice(0,-2));setMessage(text);}
    }finally{if(request===generation.current)setBusy(false);}
  }

  return <section className={`diary-ai ${embedded?"diary-ai-embedded":""}`} aria-label="Private journal AI companion">
    {!embedded&&<div className="diary-ai-heading"><div className="diary-ai-icon"><HeartHandshake size={19}/></div><div><h4>Reflect with EduNova AI</h4><p>A thoughtful conversation about what you wrote, with responses from the configured AI model.</p></div></div>}
    {!embedded&&<div className="diary-ai-controls"><label>Choose a saved journal entry
      <select value={entryId} disabled={busy} onChange={event=>setEntryId(event.target.value)}>
        {entries.length===0&&<option value="">Save an entry first</option>}
        {entries.map(entry=><option key={entry.id} value={entry.id}>{new Date(entry.created_at).toLocaleString()} · {entry.content.slice(0,45)}</option>)}
      </select></label></div>}
    <div className="diary-ai-transcript" role="log" aria-label="Encrypted journal AI messages" aria-live="polite">
      {!entryId?<p className="diary-ai-empty">Save a private reflection above to begin a conversation.</p>:
        turns.length===0?<p className="diary-ai-empty">You can share what happened, explore a feeling, or ask one question about this entry.</p>:
        turns.map((turn,index)=><article key={turn.id??`${turn.role}-${index}`} className={`diary-ai-turn ${turn.role}`}><small>{turn.role==='student'?'You':'EduNova AI'}</small><p>{turn.body||'Thinking…'}</p></article>)}
      <div ref={bottom}/>
    </div>
    <form className="diary-ai-composer" onSubmit={send}>
      <label className="diary-ai-consent"><input type="checkbox" checked={consent} onChange={event=>setConsent(event.target.checked)}/><span>I agree to send the selected journal entry and this conversation to the configured external AI provider for a reply. Do not include details you don't want to share.</span></label>
      <div className="diary-ai-inputrow"><textarea aria-label="Message to journal companion" maxLength={1800} rows={2} value={message} disabled={!entryId||busy} onChange={event=>setMessage(event.target.value)} placeholder="Something happened today, and I'd like to talk about it…"/><button type="submit" disabled={!entryId||!consent||!message.trim()||busy} aria-label="Send to AI companion">{busy?<LoaderCircle size={18} className="diary-ai-spin"/>:<Send size={19}/>}</button></div>
    </form>
    {error&&<div className="diary-ai-error" role="alert">{error}</div>}
    <p className="diary-ai-privacy"><LockKeyhole size={14}/> Replies are generated by AI, not prewritten. Saved exchanges are encrypted in your account. This is not a crisis service or real-time human monitoring; seek a trusted adult or emergency services if you are unsafe.</p>
  </section>;
}
