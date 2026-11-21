import { useEffect, useState } from "react";
import { getOptions, submitStudent } from "./api.js";

const GRADES = {
  primary: [
    ["1st primary", "1st primary"],
    ["2nd primary", "2nd primary"],
    ["3rd primary", "3rd primary"],
    ["4th primary", "4th primary"],
    ["5th primary", "5th primary"],
    ["6th primary", "6th primary"],
  ],
  high_school: [
    ["7th grade", "7th grade"],
    ["8th grade", "8th grade"],
    ["9th grade", "9th grade"],
    ["10th grade", "10th grade"],
    ["11th grade", "11th grade"],
    ["12th grade", "12th grade"],
  ],
};

const FIELDS = {
  primary: ["General studies"],
  high_school: [
    "Common core",
    "Experimental sciences",
    "Mathematics",
    "Literature",
    "Economics and management",
    "Technology",
    "Computer science",
    "Science",
    "Arts",
  ],
};

const INITIAL = {
  full_name: "", age: "", contact: "", school: "", school_level: "", grade_level: "",
  field_of_study: "",
  other_hobbies: "", needs_details: "", difficult_subjects: "", difficulty_level: 3,
  help_wanted: "", hobbies: [], special_needs: [], study_problems: [],
  difficult_subject_ids: [], help_type_ids: [], consent: false,
};
function ScrollableCheckMenu({ items, selected, onChange, placeholder, exclusiveLabel }) {
  const exclusiveId = exclusiveLabel
    ? items.find((item) => item.label === exclusiveLabel)?.id
    : undefined;

  const toggle = (id) => {
    if (selected.includes(id)) return onChange(selected.filter((x) => x !== id));
    if (id === exclusiveId) return onChange([id]);
    onChange([...selected.filter((x) => x !== exclusiveId), id]);
  };

  const labels = items
    .filter((item) => selected.includes(item.id))
    .map((item) => item.label);

  return (
    <details className="scroll-menu">
      <summary>
        <span>{labels.length ? labels.join(", ") : placeholder}</span>
        <span className="scroll-menu-arrow" aria-hidden="true">⌄</span>
      </summary>
      <div className="scroll-menu-options">
        {items.length ? items.map((item) => (
          <label key={item.id}>
            <input
              type="checkbox"
              checked={selected.includes(item.id)}
              onChange={() => toggle(item.id)}
            />
            {item.label}
          </label>
        )) : <p className="scroll-menu-empty">No options available</p>}
      </div>
    </details>
  );
}

export default function StudentForm() {
  const [opts, setOpts] = useState({
    hobbies: [], special_needs: [], study_problems: [], subjects: [], help_types: [],
  });
  const [form, setForm] = useState(INITIAL);
  const [status, setStatus] = useState({ type: "", text: "" });
  const [sending, setSending] = useState(false);

  useEffect(() => {
    getOptions().then(setOpts).catch(() => setStatus({ type: "error", text: "Unable to load the form." }));
  }, []);

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }));
  const setList = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));
  const grades = GRADES[form.school_level] || [];
  const fields = FIELDS[form.school_level] || [];
  const subjects = opts.subjects.filter((subject) => subject.school_level === form.school_level);

  async function onSubmit(e) {
    e.preventDefault();
    if (!form.consent) return setStatus({ type: "error", text: "Please accept the consent." });
    setSending(true);
    try {
      await submitStudent({ ...form, age: Number(form.age), difficulty_level: Number(form.difficulty_level) });
      setStatus({ type: "ok", text: "Thank you! Your response has been saved." });
      setForm(INITIAL);
    } catch {
      setStatus({ type: "error", text: "An error occurred while sending. Please try again." });
    } finally {
      setSending(false);
    }
  }

  return (
    <form onSubmit={onSubmit}>
      <fieldset>
        <legend>1. Personal information</legend>
        <label>Full name *<input required value={form.full_name} onChange={set("full_name")} /></label>
        {/* min lowered to 5 so primary-school students (about 6-11) can answer */}
        <label>Age *<input required type="number" min="5" max="99" value={form.age} onChange={set("age")} /></label>
        <label>Email or phone<input value={form.contact} onChange={set("contact")} /></label>
      </fieldset>

      <fieldset>
        <legend>2. Education</legend>
        <label>School / institution *<input required value={form.school} onChange={set("school")} /></label>
        <label>School level *
          <select required value={form.school_level}
            onChange={(e) => setForm((f) => ({
              ...f,
              school_level: e.target.value,
              grade_level: "",
              field_of_study: "",
              difficult_subject_ids: [], // subjects depend on the school level
            }))}>
            <option value="">— Select —</option>
            <option value="primary">Primary school</option>
            <option value="high_school">High school</option>
          </select>
        </label>
        <label>Grade / year *
          <select required value={form.grade_level} onChange={set("grade_level")} disabled={!form.school_level}>
            <option value="">— Select —</option>
            {grades.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
          </select>
        </label>
        <label>Field of study
          <select value={form.field_of_study} onChange={set("field_of_study")} disabled={!form.school_level}>
            <option value="">— Select —</option>
            {fields.map((field) => <option key={field}>{field}</option>)}
          </select>
        </label>
      </fieldset>

      <fieldset>
        <legend>3. Hobbies</legend>
        <p className="field-hint">Choose one or more hobbies. If yours is not listed, add it below.</p>
        <ScrollableCheckMenu
          items={opts.hobbies}
          selected={form.hobbies}
          onChange={setList("hobbies")}
          placeholder="Select one or more hobbies"
        />
        <label>Other hobbies (optional)<input value={form.other_hobbies} onChange={set("other_hobbies")} /></label>
      </fieldset>

      <fieldset>
        <legend>4. Special needs (optional)</legend>
        <p className="field-hint">Choose one or more needs, or select “None”. If a need is not listed, describe it below.</p>
        <ScrollableCheckMenu
          items={opts.special_needs}
          selected={form.special_needs}
          onChange={setList("special_needs")}
          placeholder="Select one or more special needs"
          exclusiveLabel="None"
        />
        <label>Other special need or details (optional)<textarea rows="3" value={form.needs_details} onChange={set("needs_details")} /></label>
      </fieldset>

      <fieldset>
        <legend>5. Study difficulties</legend>
        <ScrollableCheckMenu
          items={opts.study_problems}
          selected={form.study_problems}
          onChange={setList("study_problems")}
          placeholder="Select study problems"
        />
        <label className="menu-label">Most difficult subjects</label>
        <ScrollableCheckMenu
          items={subjects}
          selected={form.difficult_subject_ids}
          onChange={setList("difficult_subject_ids")}
          placeholder={form.school_level ? "Select difficult subjects" : "Select a school level first"}
        />
        <label>Overall difficulty level: {form.difficulty_level}/5
          <input type="range" min="1" max="5" value={form.difficulty_level} onChange={set("difficulty_level")} />
        </label>
      </fieldset>

      <fieldset>
        <legend>6. Support you would like</legend>
        <ScrollableCheckMenu
          items={opts.help_types}
          selected={form.help_type_ids}
          onChange={setList("help_type_ids")}
          placeholder="Select the help you need"
        />
        <label>Anything else? (optional)<textarea rows="3" value={form.help_wanted} onChange={set("help_wanted")} /></label>
      </fieldset>

      <label className="consent">
        <input type="checkbox" checked={form.consent} onChange={(e) => setForm((f) => ({ ...f, consent: e.target.checked }))} />
        I agree that this information may be used to support me. *
      </label>

      <button disabled={sending}>{sending ? "Sending…" : "Submit"}</button>
      {status.text && <p className={`msg ${status.type}`}>{status.text}</p>}
    </form>
  );
}
