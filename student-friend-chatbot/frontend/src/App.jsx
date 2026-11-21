import { useEffect, useRef, useState } from 'react';

export default function App() {
  const [studentId, setStudentId] = useState('');
  const [started, setStarted] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const end = useRef(null);

  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth' }); }, [messages, loading]);

  async function start() {
    if (!studentId.trim()) return;
    try {
      const r = await fetch(`/api/history/${studentId}`);
      setMessages(await r.json());
      setStarted(true);
    } catch { setError('Cannot reach the server.'); }
  }

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput(''); setError(''); setLoading(true);
    setMessages((m) => [...m, { role: 'user', content: text }]);
    try {
      const r = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ studentId, message: text }),
      });
      const data = await r.json();
      if (!r.ok) throw new Error(data.error);
      setMessages((m) => [...m, { role: 'assistant', content: data.reply }]);
    } catch (e) { setError(e.message || 'Message not sent. Try again.'); }
    setLoading(false);
  }

  if (!started) {
    return (
      <main className="login">
        <h1>Hey, I'm here for you.</h1>
        <p>Talk to me about school, stress, friends, anything.</p>
        <input value={studentId} onChange={(e) => setStudentId(e.target.value)}
               placeholder="Your student ID" onKeyDown={(e) => e.key === 'Enter' && start()} />
        <button onClick={start}>Start chatting</button>
        {error && <p className="error">{error}</p>}
      </main>
    );
  }

  return (
    <main className="chat">
      <header>Your friend</header>
      <section className="list" aria-live="polite">
        {messages.length === 0 && <p className="empty">Say hi. What's on your mind today?</p>}
        {messages.map((m, i) => <div key={i} className={`bubble ${m.role}`}>{m.content}</div>)}
        {loading && <div className="bubble assistant">…</div>}
        {error && <p className="error">{error}</p>}
        <div ref={end} />
      </section>
      <footer>
        <input value={input} onChange={(e) => setInput(e.target.value)}
               placeholder="Write a message" onKeyDown={(e) => e.key === 'Enter' && send()} />
        <button onClick={send} disabled={loading}>Send</button>
      </footer>
    </main>
  );
}
