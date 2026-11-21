import { useEffect, useState } from 'react';

// Picture-first, mascot-led prompt builder for ages 6-8. Every question and every card can be read aloud.
const topicEmoji = { Fractions: '🍕', 'Times tables': '✖️', Shapes: '🔷', 'Word problems': '🧩', 'Story clues': '🕵️', 'New vocabulary': '🔤', 'Main idea': '💡', 'Reading fluency': '🗣️', Weather: '⛅', Space: '🚀', Plants: '🌻', Animals: '🐘', 'Building sentences': '🧱', Spelling: '🐝', Punctuation: '❓', 'Describing words': '🌈' };
const ages = [{ id: '6', icon: '6️⃣', label: '6 years' }, { id: '7', icon: '7️⃣', label: '7 years' }, { id: '8', icon: '8️⃣', label: '8 years' }, { id: '9', icon: '🎒', label: '9 or older' }];
const tricky = [{ id: 'start', icon: '🚪', label: 'I need help starting' }, { id: 'words', icon: '💬', label: 'Words are tricky' }, { id: 'numbers', icon: '🔢', label: 'Numbers are tricky' }, { id: 'challenge', icon: '🏆', label: 'Give me a challenge' }];

export function say(text) {
  if (!('speechSynthesis' in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text); u.rate = 0.85; u.pitch = 1.1; u.lang = 'en-GB';
  window.speechSynthesis.speak(u);
}

export default function PromptGame({ subjects, activityStyles, supports, level, selectedSubject, selectedSupports, onGrade, onSubject, onTopic, onActivity, onToggleSupport, onTricky, onOlder, onFinish }) {
  const keys = ['age', 'subject', 'topic', 'activity', 'helpers', ...(level >= 3 ? ['tricky'] : [])];
  const [i, setI] = useState(0);
  const [picked, setPicked] = useState([]);
  const [autoRead, setAutoRead] = useState(true);
  const key = keys[i];
  const subject = subjects.find((s) => s.id === selectedSubject) ?? subjects[0];
  const q = {
    age: { say: 'Hi, I’m Foxy! How old are you?', multi: false, opts: ages },
    subject: { say: 'What do you want to explore today?', multi: false, opts: subjects.map((s) => ({ id: s.id, icon: s.emoji, label: s.name })) },
    topic: { say: `Yay! What part of ${subject.name} sounds fun?`, multi: false, opts: subject.topics.map((t) => ({ id: t, icon: topicEmoji[t] ?? '✨', label: t })) },
    activity: { say: 'How do you want to learn it?', multi: false, opts: activityStyles.map((a) => ({ id: a.id, icon: a.icon, label: a.label })) },
    helpers: { say: 'What helps you learn? Pick any, or none!', multi: true, opts: supports.map((s) => ({ id: s.id, icon: s.icon, label: s.label })) },
    tricky: { say: 'Is anything feeling tricky today?', multi: true, opts: tricky },
  }[key];

  useEffect(() => { setPicked([]); if (autoRead) say(q.say); return () => window.speechSynthesis?.cancel(); }, [key]); // eslint-disable-line

  function pick(o) {
    say(o.label);
    setPicked((p) => (q.multi ? (p.includes(o.id) ? p.filter((x) => x !== o.id) : [...p, o.id]) : [o.id]));
  }

  function next() {
    const [id] = picked;
    if (key === 'age') { if (id === '9') return onOlder(); onGrade({ 6: 1, 7: 2, 8: 3 }[id]); }
    if (key === 'subject') { onSubject(id); }
    if (key === 'topic') onTopic(id);
    if (key === 'activity') onActivity(id);
    if (key === 'helpers') selectedSupports.filter((s) => !picked.includes(s)).concat(picked.filter((s) => !selectedSupports.includes(s))).forEach(onToggleSupport);
    if (key === 'tricky') onTricky(picked);
    i + 1 < keys.length ? setI(i + 1) : onFinish();
  }

  const canNext = q.multi || picked.length > 0;
  return (
    <div className="kid-game">
      <div className="kid-stars" aria-label={`Question ${i + 1} of ${keys.length}`}>{keys.map((k, n) => <span key={k} className={n <= i ? 'on' : ''}>⭐</span>)}</div>
      <div className="mascot-row">
        <div className="mascot" aria-hidden="true">🦊</div>
        <div className="mascot-bubble" role="status" aria-live="polite" id="challenge-title">{q.say}</div>
        <button className="read-btn" onClick={() => say(q.say)} aria-label="Read the question to me">🔊</button>
        <button className="read-btn" onClick={() => { setAutoRead((a) => !a); window.speechSynthesis?.cancel(); }} aria-pressed={autoRead} aria-label="Turn automatic reading on or off">{autoRead ? '🔔' : '🔕'}</button>
      </div>
      <div className="kid-grid" role="group" aria-label="Choose an answer">
        {q.opts.map((o) => (
          <button key={o.id} className={`kid-card ${picked.includes(o.id) ? 'chosen' : ''}`} aria-pressed={picked.includes(o.id)} onClick={() => pick(o)}>
            <span className="kid-icon" aria-hidden="true">{o.icon}</span><span className="kid-label">{o.label}</span>
            {picked.includes(o.id) && <span className="kid-tick" aria-hidden="true">✓</span>}
          </button>
        ))}
      </div>
      <div className="quest-actions">
        {i > 0 && <button className="secondary-button" onClick={() => setI(i - 1)}>← Back</button>}
        <button className="primary-button modal-submit kid-next" disabled={!canNext} onClick={next}>{i + 1 === keys.length ? 'All done! ✨' : 'Next'} <span aria-hidden="true">→</span></button>
        {q.multi && picked.length === 0 && <span className="kid-skip-note">You can skip this one.</span>}
      </div>
    </div>
  );
}
