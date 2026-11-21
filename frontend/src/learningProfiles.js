// Learning supports: each one changes BOTH the prompt sent to the RAG pipeline and the UI itself.
export const accessSupports = [
  { id: 'focus', label: 'Calm focus mode', icon: '🎯', rule: 'Keep every step to 2 short sentences. Show one task at a time and include a quick movement or brain-break idea between activities. Never use timers.' },
  { id: 'dyslexia', label: 'Easy-read letters', icon: '🔤', rule: 'Use short, common words and one idea per line. Avoid look-alike words (b/d, was/saw). Phrase text so it sounds natural when read aloud. Prefer pictures over long text.' },
  { id: 'numbers', label: 'Number helper', icon: '🔢', rule: 'Show numbers with real objects, groups or a number line. Do one calculation at a time. Never rely on memorised facts or speed.' },
  { id: 'readaloud', label: 'Read it to me', icon: '🔊', rule: 'Write so the text sounds natural when read aloud: short sentences, no symbols or tables that only work on screen.' },
  { id: 'calm', label: 'Calm colours', icon: '🌙', rule: 'Keep the tone quiet and gentle, with no exclamation-heavy or exciting language.' },
];

export const trickyOptions = [
  { id: 'start', label: 'I don’t know where to start', rule: 'Begin with the very first step and a worked example.' },
  { id: 'words', label: 'The words are confusing', rule: 'Explain every new word in simple language with an example.' },
  { id: 'numbers', label: 'Numbers feel hard', rule: 'Use objects and pictures before any symbols.' },
  { id: 'challenge', label: 'I want a challenge', rule: 'End with one stretch question just above my level.' },
];

// Maps selected supports to CSS classes applied on the app shell (see access.css).
export function accessClasses(ids) {
  return ids.filter((id) => accessSupports.some((s) => s.id === id)).map((id) => `access-${id}`).join(' ');
}

// Dyscalculia / dyslexia / ADHD-friendly game types are preferred by the prompt.
export function preferredGames(ids) {
  if (ids.includes('numbers')) return 'order or choice with pictures (no timed or mental-maths-only games)';
  if (ids.includes('dyslexia')) return 'match (picture-to-word) or choice with very short options';
  if (ids.includes('focus')) return 'one short choice question';
  return 'choice, order or match';
}
