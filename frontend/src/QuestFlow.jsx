import { useEffect, useMemo, useRef, useState } from 'react';
import GameRenderer from './GameRenderer.jsx';
import { buildPrompt, questionTier } from './promptBuilder.js';

// Pip's voice (browser speech). A token stops old sentence chains when a new read starts.
export function say(text, onEnd) {
  if (!('speechSynthesis' in window)) return onEnd?.();
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text.replace(/[\u{1F300}-\u{1FAFF}\u2600-\u27BF]/gu, ''));
  u.rate = 0.85; u.pitch = 1.1; u.lang = 'en-GB'; u.onend = () => onEnd?.();
  window.speechSynthesis.speak(u);
}
const topicEmoji = { Fractions: '🍕', 'Times tables': '✖️', Shapes: '🔷', 'Word problems': '🧩', 'Story clues': '🕵️', 'New vocabulary': '🔤', 'Main idea': '💡', 'Reading fluency': '🗣️', Weather: '⛅', Space: '🚀', Plants: '🌻', Animals: '🐘', 'Building sentences': '🧱', Spelling: '🐝', Punctuation: '❓', 'Describing words': '🌈', Colours: '🎨', Drawing: '✏️', Patterns: '🔶', Sculpting: '🏺' };
const look = { maths: ['Numbers', 'peach', 'peach-strong'], reading: ['Stories & clues', 'brand', 'brand'], science: ['Our planet', 'mint', 'mint-strong'], english: ['Words & writing', 'lemon', 'lemon-strong'], art: ['Draw & create', 'sky', 'brand'] };
const helpers = [
  ['short-steps', '🪜', 'One small step at a time', 'Short steps, one idea each'], ['dyslexia', '🔎', 'Easy-to-read words', 'Bigger letters, more space'],
  ['numbers', '🔢', 'Pictures for numbers', 'Blocks & number lines'], ['readaloud', '🔊', 'Read it to me', 'Pip reads out loud'],
  ['focus', '⏱️', 'Short bursts', 'Little breaks to wiggle'], ['calm', '🌙', 'Calm colours', 'Softer, quieter look'],
];
const clean = (t) => t.replace(/[#*_`]/g, '').trim();
const sentencesOf = (t) => t.match(/[^.!?]+[.!?]+["”']?\s*/g)?.map((s) => s.trim()) ?? [t];

export default function QuestFlow({ name, subjects, activityStyles, supportDefs, selectedSupports, onToggleSupport, xp, level, progress, grade, streak, initialSubject, onClose, onFinish }) {
  const [step, setStep] = useState(0);
  const [subjId, setSubjId] = useState(initialSubject);
  const [surprise, setSurprise] = useState(false);
  const [topic, setTopic] = useState('');
  const [own, setOwn] = useState('');
  const [styleId, setStyleId] = useState('quest');
  const [stage, setStage] = useState(0);
  const [data, setData] = useState(null);
  const [err, setErr] = useState('');
  const [idea, setIdea] = useState(0);
  const [sIdx, setSIdx] = useState(-1);
  const [fs, setFs] = useState(1);
  const [sp, setSp] = useState(0);
  const [pick, setPick] = useState(null);
  const [checked, setChecked] = useState(false);
  const [hint, setHint] = useState(false);
  const [correct, setCorrect] = useState(false);
  const tok = useRef(0);

  const has = (id) => selectedSupports.includes(id);
  const subject = subjects.find((s) => s.id === subjId) ?? subjects[0];
  const concept = topic === '__own' ? own.trim() : topic;
  const topicIdx = subject.topics.indexOf(topic);
  const unlocked = Math.min(subject.topics.length, level);
  const stars = (i) => Math.max(0, Math.min(3, Math.round(progress[subject.id] / 25) - i));
  const suggested = subject.topics.findIndex((_, i) => i < unlocked && stars(i) < 3);
  const style = activityStyles.find((a) => a.id === styleId);
  const game = data?.game;
  const isChoice = game && (!game.type || game.type === 'choice');
  const ideas = useMemo(() => {
    const text = clean(data?.answer_text ?? '');
    const paras = text.split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
    if (paras.length > 1) return paras.slice(0, 6);
    const s = sentencesOf(text), out = [];
    for (let i = 0; i < s.length; i += 3) out.push(s.slice(i, i + 3).join(' '));
    return out.length ? out : [text];
  }, [data]);
  const sents = sentencesOf(ideas[idea] ?? '');

  const prompt = buildPrompt({
    grade, subject: subject.name, concept: concept || subject.next, progress: progress[subject.id], level, xp, mode: style.label, supports: selectedSupports, tricky: [],
    supportRules: selectedSupports.map((id) => supportDefs.find((x) => x.id === id)?.rule).filter(Boolean),
  });
  const tier = { sprout: 'Sprout ⭐☆☆', explorer: 'Explorer ⭐⭐☆', pathfinder: 'Pathfinder ⭐⭐⭐' }[questionTier(level)];

  const pipLine = [
    surprise ? `I picked ${subject.name} for you! Tap Next if you like it, or choose another.` : `Hi ${name}! I’m Pip. What would you like to explore today?`,
    'Great pick! These islands fit your level. The glowing one is a good place to start.',
    `Now the fun part! How would you like to learn about ${concept || subject.next}?`,
    'Everyone’s brain learns in its own way! Pick any helpers you like. You can change them any time.',
    'Here’s your learning wish! I’ll use it to find the best lesson for you.',
    `I’m reading the Grade ${grade} ${subject.name} book for you. This only takes a moment. Take a deep breath! 🌬️`,
    'One idea at a time. Tap “Got it!” when you’re ready for the next one. Take your time!',
    checked ? `${correct ? '🌟 You did it! ' : '💛 That’s okay! '}${game?.explanation ?? ''}` : `${game?.question ?? ''} Take your time. There’s no timer!`,
    'You did it! Every try makes your brain stronger. I’m so proud of you!',
  ][step];

  useEffect(() => { if (has('readaloud')) say(pipLine); }, [step, checked, surprise]); // eslint-disable-line
  useEffect(() => () => window.speechSynthesis?.cancel(), []);
  useEffect(() => {
    if (step !== 5) return undefined;
    const a = setTimeout(() => setStage((s) => Math.max(s, 1)), 700), b = setTimeout(() => setStage((s) => Math.max(s, 2)), 1900);
    return () => { clearTimeout(a); clearTimeout(b); };
  }, [step]);

  function readIdea() {
    const t = ++tok.current; let i = 0;
    const next = () => { if (t !== tok.current || i >= sents.length) { if (t === tok.current) setSIdx(-1); return; } setSIdx(i); say(sents[i], () => { i += 1; next(); }); };
    next();
  }
  function choose(id) {
    if (id === 'surprise') { const pool = subjects.filter((s) => s.id !== 'surprise'); setSubjId(pool[Math.floor(Math.random() * pool.length)].id); setSurprise(true); } else { setSubjId(id); setSurprise(false); }
    setTopic('');
  }
  async function ask() {
    setStep(5); setStage(0); setErr(''); setData(null); setIdea(0); setPick(null); setChecked(false); setHint(false);
    try {
      const res = await fetch('/api/learn', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ generated_prompt: prompt, grade_level: grade }) });
      if (!res.ok) throw new Error((await res.json().catch(() => ({}))).detail || 'Pip is taking a little break. Please try again soon.');
      setData(await res.json()); setStage(4); setStep(6);
    } catch (e) {
      setErr(e instanceof TypeError ? 'I couldn’t reach my books. Please ask a grown-up to check the connection, then try again.' : e.message);
    }
  }
  const finishGame = (ok) => { setCorrect(ok); setStep(8); };
  const warn = data && (data.has_hallucinations || !data.is_grounded);
  const lastIdea = idea >= ideas.length - 1;
  const gain = correct ? 10 : 0, newXp = xp + gain, newLevel = Math.floor(newXp / 100) + 1;
  const newStars = Math.min(3, (topicIdx >= 0 ? stars(topicIdx) : 0) + (correct ? 1 : 0));

  const stones = step <= 5 ? ['Subject', 'Island', 'Style', 'Helpers', 'Wish'] : ['Learn', 'Try', 'Play', 'Win'];
  const cur = step <= 4 ? step : step === 5 ? 5 : step === 6 ? 0 : step === 7 ? 1 : 4;
  const bar = (left, note, right) => <div className="q-actions"><div>{left}</div><span>{note}</span><div>{right}</div></div>;
  const back = (to) => <button className="q-btn alt" onClick={() => setStep(to ?? step - 1)}>← Back</button>;
  const next = (label, onClick, disabled) => <button className="q-btn" disabled={disabled} onClick={onClick ?? (() => setStep(step + 1))}>{label}</button>;
  const rush = 'No rush — you’re in charge of your adventure.';

  return (
    <div className={`quest ${has('calm') ? 'calm' : ''}`} role="dialog" aria-modal="true" aria-label="Learning quest">
      <header className="q-top">
        <div className="q-left"><button className="q-close" onClick={onClose} aria-label="Close quest">✕</button><div className="q-brand"><span className="q-logo">b</span><span>brightpath</span></div></div>
        <div className="q-stones" aria-label="Progress">{stones.map((s, i) => <div key={s} className={`q-stone ${i < cur ? 'done' : i === cur ? 'now' : ''}`}><i>{i < cur ? '✓' : i === cur ? '🦊' : ''}</i><span>{s}</span></div>)}</div>
        <div className="q-pills">
          <button className={`q-pill ${has('readaloud') ? 'on' : ''}`} aria-pressed={has('readaloud')} onClick={() => { if (!has('readaloud')) say(pipLine); onToggleSupport('readaloud'); }}><span>🔊</span><span>Read to me</span></button>
          <button className={`q-pill ${has('calm') ? 'on' : ''}`} aria-pressed={has('calm')} onClick={() => onToggleSupport('calm')}><span>🌙</span><span>Calm</span></button>
          <div className="q-pill xp"><span>⭐</span><span>{xp} XP</span></div>
        </div>
      </header>

      <div className="q-body">
        <aside className="q-pip"><div className="q-pip-avatar" aria-hidden="true">🦊</div><div className="q-pip-says" role="status" aria-live="polite">{pipLine}</div></aside>
        <main className="q-content">
          {step === 0 && <>
            <h1>What do you want to explore today?</h1><p className="q-sub">Tap a picture. There’s no wrong choice!</p>
            <div className="q-grid3" role="group" aria-label="Subjects">
              {[...subjects, { id: 'surprise', name: 'Surprise!', emoji: '🎲' }].map((s) => { const l = look[s.id] ?? ['Pip picks for you', 'surface', 'brand']; const sel = s.id === 'surprise' ? surprise : subjId === s.id && !surprise;
                return <button key={s.id} className={`q-subject ${sel ? 'sel' : ''}`} style={{ '--tint': `var(--${l[1]}-tint)`, '--fill': `var(--${l[2]})` }} aria-pressed={sel} onClick={() => choose(s.id)}>
                  <span className="top"><span className="title"><span className="q-emoji" aria-hidden="true">{s.emoji}</span><span><b>{s.name}</b><small>{l[0]}</small></span></span>{sel && <span className="q-check" aria-hidden="true">✓</span>}</span>
                  {s.id !== 'surprise' ? <span className="q-bar"><span style={{ width: `${progress[s.id]}%` }} /></span> : <span className="q-bar" />}</button>; })}
            </div>
          </>}

          {step === 1 && <>
            <h1>Pick your {subject.name} island</h1><p className="q-sub">Stars show how much you’ve explored. Locked islands open when you earn more XP.</p>
            <div className="q-map" role="group" aria-label="Islands">
              {subject.topics.map((t, i) => { const locked = i >= unlocked; return <button key={t} className={`q-island ${topic === t ? 'sel' : ''} ${locked ? 'locked' : ''}`} disabled={locked} aria-pressed={topic === t} onClick={() => { setTopic(t); setOwn(''); say(t); }}>
                {i === suggested && <span className="q-suggest">Pip suggests ✨</span>}<span className="disc" aria-hidden="true">{locked ? '🔒' : topicEmoji[t] ?? '✨'}</span><b>{t}</b><small>{locked ? 'Earn more XP' : '⭐'.repeat(stars(i)) + '☆'.repeat(3 - stars(i))}</small></button>; })}
            </div>
            <input className="q-own" aria-label="Type your own topic" placeholder="✏️  Or type something you’re curious about…" value={own} onChange={(e) => { setOwn(e.target.value); setTopic(e.target.value ? '__own' : ''); }} />
          </>}

          {step === 2 && <>
            <h1>How should we learn it?</h1><p className="q-sub">Pick the kind of activity that sounds fun.</p>
            <div className="q-grid3" role="group" aria-label="Activity style">
              {activityStyles.map((a) => <button key={a.id} className={`q-style ${styleId === a.id ? 'sel' : ''}`} aria-pressed={styleId === a.id} onClick={() => { setStyleId(a.id); say(a.label); }}>
                <span className="big" aria-hidden="true">{a.icon}</span><b>{a.label}</b><small>{a.description}</small>{styleId === a.id && <span className="q-chosen">✓ Chosen</span>}</button>)}
            </div>
            <div className="q-note"><span>🌟</span>{progress[subject.id] >= 50 ? `You’ve explored a lot of ${subject.name} already — we’ll build on what you know.` : `Let’s start with the basics of ${subject.name} together.`}</div>
          </>}

          {step === 3 && <>
            <h1>What helps you learn?</h1><p className="q-sub">Choose any magic helpers. There are no wrong choices.</p>
            <div className="q-helpers" role="group" aria-label="Learning helpers">
              {helpers.map(([id, icon, label, sub]) => <button key={id} className={`q-helper ${has(id) ? 'on' : ''}`} aria-pressed={has(id)} onClick={() => { onToggleSupport(id); say(label); }}>
                <span className="q-emoji" aria-hidden="true">{icon}</span><span className="tx"><b>{label}</b><small>{sub}</small></span><span className="q-toggle" aria-hidden="true"><i /></span></button>)}
            </div>
            <div className="q-note">🔒 These are learning preferences, not a test. Your grown-up can help you choose.</div>
          </>}

          {step === 4 && <>
            <h1>Your learning wish is ready!</h1><p className="q-sub">Everything you picked is on this scroll. Want to change something? Just tap it.</p>
            <div className="q-wish"><div className="q-scroll">
              {[['📚', 'I want to learn', `${concept || subject.next} in ${subject.name}`, 1], [style.icon, 'I like to learn with', style.label, 2], ['⭐', 'My level', tier, null],
                ['🧰', 'My helpers', selectedSupports.length ? helpers.filter(([id]) => has(id)).map(([, i, l]) => `${i} ${l}`).join('  ') : 'None — and that’s okay!', 3]].map(([e, k, v, to]) =>
                <div className="q-wishrow" key={k}><span className="q-emoji" aria-hidden="true">{e}</span><span className="tx"><small>{k}</small><b>{v}</b></span>{to !== null && <button className="q-edit" aria-label={`Change ${k}`} onClick={() => setStep(to)}>✏️</button>}</div>)}
            </div><aside className="q-grown"><b className="nunito">👀 Grown-up view</b><pre>{`What Pip sends to the tutor:\n\n${prompt}`}</pre></aside></div>
          </>}

          {step === 5 && <>
            <h1>Pip is making your lesson…</h1>
            <div aria-live="polite">{[`Found your ${concept || subject.next} island`, `Opened the Grade ${grade} ${subject.name} book`, 'Writing your quest in easy words', 'Building your game'].map((l, i) => { const st = stage > i ? 'done' : stage === i && !err ? 'now' : '';
              return <div key={l} className={`q-stage ${st}`}><i>{st === 'done' ? '✓' : st === 'now' ? '…' : '○'}</i>{l}</div>; })}</div>
            {err ? <div className="q-err" role="alert">{err}</div> : <div className="q-float" aria-hidden="true"><span>📚</span><span>📖</span><span>✨</span><span>🧩</span></div>}
          </>}

          {step === 6 && <>
            <h1>{concept || subject.next} {topicEmoji[topic] ?? '✨'}</h1>
            {warn && <div className="q-warn" role="status">This answer may need a grown-up or teacher to check it.</div>}
            <section className="q-lesson" style={{ '--fs': fs, '--sp': `${sp}em` }}>
              <div className="q-dots" aria-label={`Idea ${idea + 1} of ${ideas.length}`}>{ideas.map((_, i) => <i key={i} className={i === idea ? 'on' : ''} />)}<span>&nbsp; Idea {idea + 1} of {ideas.length}</span></div>
              <div className="q-lbody"><div className="q-sents" aria-live="polite">{sents.map((s, j) => <p key={`${idea}-${j}`} className={`q-sent ${(sIdx === -1 ? j === 0 : j === sIdx) ? 'ruler' : ''}`} style={{ margin: 0 }}>{s}</p>)}</div>
                <div className="q-pic" aria-hidden="true">{topicEmoji[topic] ?? '✨'}<em>{concept || subject.next}</em></div></div>
              <div className="q-tools"><button className="q-pill" onClick={readIdea}><span>🔊</span><span>Read it</span></button>
                <button className="q-pill" onClick={() => setFs((f) => (f >= 1.3 ? 1 : f + 0.15))}><span>Aa</span><span>Bigger</span></button>
                <button className="q-pill" onClick={() => setSp((s) => (s >= 0.1 ? 0 : s + 0.05))}><span>↔</span><span>More space</span></button>
                {data?.sources?.length > 0 && <span className="q-src">📖 From the Grade {grade} {subject.name} book</span>}</div>
            </section>
          </>}

          {step === 7 && game && <>
            <h1>Show what you discovered!</h1>
            {isChoice ? <>
              <div className="q-qbox"><span aria-hidden="true">🎮</span>{game.question}</div>
              <div className="q-answers" role="group" aria-label="Choose your answer">{game.choices.map((c, i) => <button key={`${i}-${c}`} className={`q-ans ${pick === i ? 'sel' : ''} ${checked && i === game.correct_index ? 'right' : ''}`} aria-pressed={pick === i} onClick={() => { if (!checked) { setPick(i); say(c); } }}><span className="let">{String.fromCharCode(65 + i)}</span>{c}</button>)}</div>
              {hint && !checked && <div className="q-hint" role="status">💡 {game.hint}</div>}
            </> : <GameRenderer game={game} onDone={finishGame} />}
          </>}

          {step === 8 && <div className="q-win">
            {[...Array(16)].map((_, i) => <span key={i} className="q-confetti" aria-hidden="true" style={{ left: `${((20 + 83 * i) / 1280) * 100}%`, top: `${i % 2 ? 237 + 7 * (i - 1) : 100 + 7 * i}px`, width: [12, 17, 22][i % 3], height: [12, 17, 22][i % 3], background: ['var(--peach-strong)', 'var(--lemon-strong)', 'var(--mint-strong)', 'var(--brand)'][i % 4], opacity: 0.8 }} />)}
            <div className="party" aria-hidden="true">{correct ? '🎉' : '🌱'}</div><h1>{correct ? `You did it, ${name}!` : `Great try, ${name}!`}</h1>
            <p className="q-sub" style={{ margin: '12px 0 24px' }}>{correct ? `You learned something new about ${concept || subject.next}.` : 'Every try makes your brain stronger. Let’s have another go soon!'}</p>
            <div className="q-rewards">
              <div className="q-reward"><span className="e">⭐</span><b>{gain ? `+${gain} XP` : 'Keep going!'}</b><span className="q-bar"><span style={{ width: `${newXp % 100}%`, '--fill': 'var(--lemon-strong)' }} /></span><small>{newLevel > level ? `You reached level ${newLevel}!` : `${100 - (newXp % 100)} XP to level ${newLevel + 1}`}</small></div>
              <div className="q-reward"><span className="e">{topicEmoji[topic] ?? '✨'}</span><b>{'⭐'.repeat(newStars) + '☆'.repeat(3 - newStars)}</b><small>{concept || subject.next} island: {newStars} {newStars === 1 ? 'star' : 'stars'}!</small></div>
              <div className="q-reward"><span className="e">🔥</span><b>{streak} days</b><small>Your learning streak</small></div>
            </div>
            {newLevel > level && subject.topics[level] && <div className="q-unlock" style={{ marginTop: 20 }}>🏝️ New island unlocked: {subject.topics[level]}</div>}
          </div>}
        </main>
      </div>

      {step === 0 && bar(<span />, rush, next('Next: pick an island →', null, !subjId))}
      {step === 1 && bar(back(), rush, next('Next →', null, !concept))}
      {step === 2 && bar(back(), rush, next('Next →'))}
      {step === 3 && bar(back(), <button className="q-link" onClick={() => setStep(4)}>Skip helpers</button>, next('Next →'))}
      {step === 4 && bar(back(), rush, next('Ask Pip ✨', ask))}
      {step === 5 && (err ? bar(back(4), '', next('Try again', ask)) : bar(<span />, 'You can wiggle your fingers while you wait 🤸', <span />))}
      {step === 6 && bar(<button className="q-btn alt" onClick={readIdea}>Say it again 🔁</button>, `Idea ${idea + 1} — no rush`,
        next(lastIdea ? (game ? 'Let’s play! →' : 'Back to my garden →') : 'Got it! Next idea →', () => { window.speechSynthesis?.cancel(); setSIdx(-1); if (!lastIdea) setIdea(idea + 1); else if (game) setStep(7); else onClose(); }))}
      {step === 7 && isChoice && bar(!checked ? <button className="q-btn alt" onClick={() => setHint(true)}>💡 Give me a hint</button> : <span />, 'No timer. Mistakes help your brain grow!',
        !checked ? next('Check my answer →', () => { setChecked(true); setCorrect(pick === game.correct_index); }, pick === null) : next('Keep going →', () => finishGame(correct)))}
      {step === 7 && !isChoice && bar(<span />, 'No timer. Mistakes help your brain grow!', <span />)}
      {step === 8 && bar(<button className="q-btn alt" onClick={() => { setStep(1); setTopic(''); setData(null); }}>Play another 🎮</button>, `Great work today, ${name}!`, next('Back to my garden →', () => onFinish(correct)))}
    </div>
  );
}
