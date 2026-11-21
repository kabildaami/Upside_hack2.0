export function buildPrompt({
  grade,
  subject,
  concept,
  progress,
  level,
  xp,
  mode,
  supports = [],
  tricky = [],
  supportRules = [],
}) {
  let prompt = `Grade ${grade} ${subject} Lesson\n`;
  prompt += `Concept: ${concept}\n`;
  prompt += `Current Progress: ${progress}%\n`;
  prompt += `Learning Level: ${level} (${xp} XP)\n`;
  prompt += `Activity Mode: ${mode}\n`;

  if (supportRules.length > 0) {
    prompt += `\nAccessibility & Learning Preferences:\n`;
    supportRules.forEach(rule => {
      prompt += `- ${rule}\n`;
    });
  }

  if (tricky.length > 0) {
    prompt += `\nAreas that feel tricky for this student:\n`;
    tricky.forEach(t => {
      prompt += `- ${t}\n`;
    });
  }

  prompt += `\nPlease provide age-appropriate, grounded learning content that is safe, supportive, and honors these preferences. No diagnosis or sensitive health questions.`;
  return prompt;
}
