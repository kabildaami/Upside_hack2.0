import { useState } from "react";
import OnboardingSelector from "./components/OnboardingSelector";
import MoodCheckInBar from "./components/MoodCheckInBar";
import AdaptiveMessage from "./components/AdaptiveMessage";
import EncouragementBanner from "./components/EncouragementBanner";
import useTelemetry from "./hooks/useTelemetry";

const API = "http://localhost:8000";

export default function App() {
  const [studentId, setStudentId] = useState("demo-student");
  const [sessionId] = useState(() => crypto.randomUUID());
  const [selected, setSelected] = useState([]);
  const [mood, setMood] = useState("ready");
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [started, setStarted] = useState(false);
  useTelemetry(studentId, sessionId);

  async function start() {
    await fetch(`${API}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, support_cards: selected }),
    });
    setStarted(true);
  }

  async function changeMood(value) {
    setMood(value);
    await fetch(`${API}/chat/mood`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, session_id: sessionId, mood: value }),
    }).catch(() => {});
  }

  async function send(event) {
    event.preventDefault();
    if (!message.trim()) return;
    const result = await fetch(`${API}/chat/turn`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_id: studentId, session_id: sessionId, message }),
    }).then((item) => item.json());
    setResponse(result);
    setMessage("");
  }

  if (!started) {
    return (
      <main className="shell">
        <h1>How can I support you?</h1>
        <p>These choices are optional and can be changed anytime.</p>
        <label>
          Student ID
          <input value={studentId} onChange={(event) => setStudentId(event.target.value)} />
        </label>
        <OnboardingSelector selected={selected} onChange={setSelected} />
        <button className="primary" type="button" onClick={start}>Start tutoring</button>
      </main>
    );
  }

  return (
    <main className="shell">
      <header>
        <h1>Adaptive Tutor</h1>
        <EncouragementBanner message={response?.encouragement} />
      </header>
      <MoodCheckInBar mood={mood} onChange={changeMood} />
      <AdaptiveMessage response={response} />
      <form className="composer" onSubmit={send}>
        <input
          aria-label="Tutoring question"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
          placeholder="Ask a question or share what feels difficult..."
        />
        <button type="submit">Send</button>
      </form>
    </main>
  );
}
