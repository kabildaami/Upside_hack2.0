export default function AdaptiveMessage({ response }) {
  if (!response) return null;
  function speak() {
    if (!("speechSynthesis" in window)) return;
    const utterance = new SpeechSynthesisUtterance(response.text);
    window.speechSynthesis.speak(utterance);
  }
  return (
    <article className="message">
      {response.alerted && (
        <div className="encouragement" role="alert">
          Your message has been flagged for trusted-adult support. You are not alone.
        </div>
      )}
      <p>{response.text}</p>
      {response.steps?.length > 0 && (
        <ol>
          {response.steps.map((step, index) => (
            <li key={index}>
              <strong>{step.title}</strong> {step.detail}
            </li>
          ))}
        </ol>
      )}
      {response.show_audio && (
        <button type="button" onClick={speak}>Listen</button>
      )}
      {response.encouragement && (
        <div className="encouragement">{response.encouragement}</div>
      )}
    </article>
  );
}
