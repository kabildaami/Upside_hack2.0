export default function MoodCheckInBar({ mood, onChange }) {
  return (
    <div className="mood-bar" aria-label="How do you feel">
      <span>How is this session feeling?</span>
      {["ready", "tired", "stressed"].map((item) => (
        <button
          type="button"
          key={item}
          className={mood === item ? "selected" : ""}
          onClick={() => onChange(item)}
        >
          {item}
        </button>
      ))}
    </div>
  );
}
