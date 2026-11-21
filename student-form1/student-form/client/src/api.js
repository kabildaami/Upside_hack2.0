export async function getOptions() {
  const r = await fetch("/api/students/options");
  if (!r.ok) throw new Error("Failed to load options");
  return r.json();
}

export async function submitStudent(data) {
  const r = await fetch("/api/students", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!r.ok) throw new Error("Failed to submit");
  return r.json();
}
