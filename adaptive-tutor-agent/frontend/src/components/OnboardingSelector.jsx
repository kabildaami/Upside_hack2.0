const cards = [
  ["adhd", "One step at a time"],
  ["dyslexia", "Plain text and audio"],
  ["low_confidence", "Warm encouragement"],
  ["tough_coursework", "Extra scaffolding"],
];

export default function OnboardingSelector({ selected, onChange }) {
  function toggle(card) {
    onChange(
      selected.includes(card)
        ? selected.filter((item) => item !== card)
        : [...selected, card],
    );
  }
  return (
    <div className="card-grid">
      {cards.map(([card, label]) => (
        <button
          className={selected.includes(card) ? "support-card selected" : "support-card"}
          key={card}
          type="button"
          onClick={() => toggle(card)}
        >
          <strong>{label}</strong>
          <span>{selected.includes(card) ? "Selected" : "Choose"}</span>
        </button>
      ))}
    </div>
  );
}
