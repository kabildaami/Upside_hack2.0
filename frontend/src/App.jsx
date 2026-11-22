import { useState } from 'react';
import PromptGame from './PromptGame.jsx';
import GameRenderer from './GameRenderer.jsx';
import { accessSupports, accessClasses, trickyOptions } from './learningProfiles.js';
import { buildPrompt } from './promptBuilder.js';

const subjects = [
  { id: 'maths', name: 'Maths', emoji: '🧮', color: 'peach', progress: 72, unit: 'Fractions & numbers', next: 'Make friends with fractions', detail: 'You’re getting really good at spotting number patterns.', topics: ['Fractions', 'Times tables', 'Shapes', 'Word problems'] },
  { id: 'reading', name: 'Reading', emoji: '📚', color: 'lavender', progress: 48, unit: 'Stories & adventures', next: 'The secret treehouse', detail: 'A new story is waiting for you to explore.', topics: ['Story clues', 'New vocabulary', 'Main idea', 'Reading fluency'] },
  { id: 'science', name: 'Science', emoji: '🔭', color: 'mint', progress: 34, unit: 'Our amazing planet', next: 'How do clouds float?', detail: 'Let’s investigate something wonderful about our world.', topics: ['Weather', 'Space', 'Plants', 'Animals'] },
  { id: 'english', name: 'English', emoji: '✏️', color: 'lemon', progress: 86, unit: 'Words & writing', next: 'Build a brilliant sentence', detail: 'Your word skills are growing every day.', topics: ['Building sentences', 'Spelling', 'Punctuation', 'Describing words'] },
];

const baseSupports = [
  { id: 'short-steps', label: 'One small step at a time', icon: '🪜', rule: 'Break the learning into short, clearly numbered steps with gentle reminders.' },
  { id: 'clear-reading', label: 'Clear, easy-to-read words', icon: '🔎', rule: 'Use plain, age-appropriate language, short sentences, and generous spacing. Avoid unnecessary jargon.' },
  { id: 'visuals', label: 'Pictures and examples', icon: '🎨', rule: 'Explain ideas with concrete visual descriptions, familiar examples, and simple analogies.' },
  { id: 'practice', label: 'Extra practice time', icon: '🌱', rule: 'Give one question at a time, allow time to think, and offer a kind hint before revealing an answer.' },
];
const learningSupports = [...baseSupports, ...accessSupports];

const activityStyles = [
  { id: 'quest', label: 'A little quest', icon: '🗺️', description: 'Solve a friendly mission' },
  { id: 'story', label: 'A silly story', icon: '🐉', description: 'Learn through an adventure' },
  { id: 'build', label: 'Make or draw', icon: '🧩', description: 'Use hands-on ideas' },
];

const navItems = [
  { id: 'home', label: 'My home', icon: '⌂' },
  { id: 'journey', label: 'My journey', icon: '✦' },
  { id: 'rewards', label: 'My rewards', icon: '♧' },
];

function App() {
  const todayLabel = new Intl.DateTimeFormat('en-GB', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  }).format(new Date()).toUpperCase();
  const [selectedSubject, setSelectedSubject] = useState('maths');
  const [activeNav, setActiveNav] = useState('home');
  const [isChallengeOpen, setIsChallengeOpen] = useState(false);
  const [questStep, setQuestStep] = useState(0);
  const [selectedTopic, setSelectedTopic] = useState('');
  const [customTopic, setCustomTopic] = useState('');
  const [selectedActivity, setSelectedActivity] = useState('quest');
  const [selectedSupports, setSelectedSupports] = useState([]);
  const [gradeLevel, setGradeLevel] = useState(4);
  const [tricky, setTricky] = useState([]);
  const [kidMode, setKidMode] = useState(true);
  const [generatedAnswer, setGeneratedAnswer] = useState('');
  const [answerSources, setAnswerSources] = useState([]);
  const [answerWarning, setAnswerWarning] = useState(false);
  const [practiceGame, setPracticeGame] = useState(null);
  const [gameChoice, setGameChoice] = useState(null);
  const [gameChecked, setGameChecked] = useState(false);
  const [isLoadingAnswer, setIsLoadingAnswer] = useState(false);
  const [requestError, setRequestError] = useState('');
  const [dailyActivities, setDailyActivities] = useState(2);
  const [experiencePoints, setExperiencePoints] = useState(230);
  const [subjectProgress, setSubjectProgress] = useState(() =>
    Object.fromEntries(subjects.map(({ id, progress }) => [id, progress])),
  );

  const subject = subjects.find((item) => item.id === selectedSubject) ?? subjects[0];
  const learningLevel = Math.floor(experiencePoints / 100) + 1;
  const chosenTopic = selectedTopic === 'Something else' ? customTopic || 'Something else' : selectedTopic;
  const learningMode = activityStyles.find(({ id }) => id === selectedActivity) ?? activityStyles[0];
  const learningPrompt = buildPrompt({
    grade: gradeLevel, subject: subject.name, concept: chosenTopic || subject.next,
    progress: subjectProgress[subject.id], level: learningLevel, xp: experiencePoints,
    mode: learningMode.label, supports: selectedSupports, tricky,
    supportRules: selectedSupports.map((id) => learningSupports.find((x) => x.id === id)?.rule).filter(Boolean),
  });
  const isMulti = !practiceGame?.type || practiceGame.type === 'choice';

  function finishGame(correct) {
    if (correct) {
      setDailyActivities((c) => Math.min(c + 1, 3));
      setSubjectProgress((p) => ({ ...p, [subject.id]: Math.min(p[subject.id] + 3, 100) }));
      setExperiencePoints((x) => x + 10);
    }
    closeChallenge();
  }

  function openChallenge() {
    setQuestStep(0);
    setSelectedTopic(subject.next);
    setCustomTopic('');
    setSelectedActivity('quest');
    setSelectedSupports([]);
    setTricky([]);
    setKidMode(true);
    setGeneratedAnswer('');
    setAnswerSources([]);
    setAnswerWarning(false);
    setPracticeGame(null);
    setGameChoice(null);
    setGameChecked(false);
    setRequestError('');
    setIsChallengeOpen(true);
  }

  function closeChallenge() {
    setIsChallengeOpen(false);
    setIsLoadingAnswer(false);
  }

  function toggleSupport(supportId) {
    setSelectedSupports((current) => current.includes(supportId)
      ? current.filter((id) => id !== supportId)
      : [...current, supportId]);
  }

  async function sendPromptToTutor() {
    setIsLoadingAnswer(true);
    setRequestError('');
    try {
      const response = await fetch('/api/learn', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ generated_prompt: learningPrompt, grade_level: gradeLevel }),
      });
      if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || 'Your learning buddy is taking a little break. Please try again soon.');
      }
      const result = await response.json();
      setGeneratedAnswer(result.answer_text);
      setAnswerSources(result.sources ?? []);
      setAnswerWarning(Boolean(result.has_hallucinations) || !result.is_grounded);
      setPracticeGame(result.game ?? null);
      setQuestStep(4);
    } catch (error) {
      setRequestError(error instanceof TypeError
        ? 'Could not reach your learning buddy. Please ask a grown-up to check the connection, then try again.'
        : error.message || 'Could not reach your learning buddy. Please try again.');
    } finally {
      setIsLoadingAnswer(false);
    }
  }

  return (
    <div className={`app-shell ${accessClasses(selectedSupports)}`}>
      <aside className="sidebar" aria-label="Main navigation">
        <a className="brand" href="#home" aria-label="BrightPath home">
          <span className="brand-mark">b</span>
          <span>brightpath<span className="brand-dot">.</span></span>
        </a>

        <div className="profile-card">
          <div className="avatar" aria-hidden="true">🦊</div>
          <div className="profile-copy">
            <span className="eyebrow">YOUR LEARNING SPACE</span>
            <strong>Hi, Alex!</strong>
            <span className="profile-level">Level {Math.floor(experiencePoints / 100) + 1} explorer · {experiencePoints} XP</span>
          </div>
          <button className="more-button" aria-label="Profile options">···</button>
        </div>

        <nav className="nav-list">
          <span className="nav-heading">MENU</span>
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${activeNav === item.id ? 'active' : ''}`}
              onClick={() => setActiveNav(item.id)}
              aria-current={activeNav === item.id ? 'page' : undefined}
            >
              <span className="nav-icon" aria-hidden="true">{item.icon}</span>
              <span>{item.label}</span>
              {item.id === 'rewards' && <span className="nav-new">2</span>}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="streak-card">
            <div className="streak-icon" aria-hidden="true">🔥</div>
            <div>
              <strong>5 day streak!</strong>
              <span>You’re on a roll</span>
            </div>
            <span className="streak-sparkle" aria-hidden="true">✦</span>
          </div>
          <button className="help-link" onClick={() => window.alert('Ask a grown-up to help you with your learning account.')}>☻ <span>Need a little help?</span></button>
          <div className="parent-note"><span aria-hidden="true">🔒</span> A safe space, just for you</div>
        </div>
      </aside>

      <main className="main-content" id="home">
        <header className="topbar">
          <div className="breadcrumbs"><span>My home</span><span className="crumb-slash">/</span><strong>{activeNav === 'home' ? 'Dashboard' : navItems.find((item) => item.id === activeNav)?.label}</strong></div>
          <div className="topbar-actions">
            <div className="today-pill"><span className="status-dot" /> All caught up</div>
            <button className="notification-button" aria-label="Notifications">♧<span className="notification-dot" /></button>
            <button className="top-avatar" aria-label="Open profile">🦊</button>
          </div>
        </header>

        <div className="page-content">
          <section className="welcome-row">
            <div>
              <div className="date-label">{todayLabel}</div>
              <h1>Ready for a little <span>adventure?</span> <span className="wave" aria-hidden="true">✦</span></h1>
              <p className="welcome-subtitle">Every small step makes your brain stronger. Let’s see what you can do today!</p>
            </div>
            <div className="daily-goal">
              <div className="goal-ring" style={{ background: `conic-gradient(#ffab74 0 ${Math.min(dailyActivities / 3, 1) * 100}%, #ffeadb ${Math.min(dailyActivities / 3, 1) * 100}% 100%)` }}><span>{dailyActivities}<span className="goal-divider">/</span>3</span></div>
              <div><strong>Daily goal</strong><span>{dailyActivities >= 3 ? 'You did it today!' : `${3 - dailyActivities} more ${3 - dailyActivities === 1 ? 'activity' : 'activities'} to go`}</span></div>
            </div>
          </section>

          <section className="hero-card" aria-label="Continue your learning">
            <div className="hero-copy">
              <div className="hero-tag"><span className="hero-tag-dot" /> YOUR NEXT BIG THING</div>
              <h2>Let’s make learning<br />an <span>adventure!</span></h2>
              <p>Pick up where you left off and earn a new star for your collection.</p>
              <button className="primary-button" onClick={openChallenge}>Continue learning <span aria-hidden="true">→</span></button>
              <div className="lesson-meta"><span>⏱ 8 min</span><span className="meta-divider" /><span>✨ Just right for you</span></div>
            </div>
            <div className="hero-art" aria-hidden="true">
              <span className="art-sun" />
              <span className="art-star star-one">✦</span><span className="art-star star-two">✧</span>
              <div className="art-cloud cloud-one" /><div className="art-cloud cloud-two" />
              <div className="art-hill hill-back" /><div className="art-hill hill-front" />
              <div className="art-book">📖</div>
              <div className="art-bubble">You’ve got<br />this! <span>☺</span></div>
            </div>
          </section>

          <section className="subjects-section">
            <div className="section-heading">
              <div><h2>Your learning garden <span aria-hidden="true">🌱</span></h2><p>Choose a subject to see how you’re growing.</p></div>
              <button className="text-button" onClick={() => setActiveNav('journey')}>See my journey <span aria-hidden="true">→</span></button>
            </div>

            <div className="subject-grid">
              {subjects.map((item) => (
                <button
                  key={item.id}
                  className={`subject-card ${item.color} ${selectedSubject === item.id ? 'selected' : ''}`}
                  onClick={() => setSelectedSubject(item.id)}
                  aria-pressed={selectedSubject === item.id}
                >
                  <span className="subject-top"><span className="subject-emoji" aria-hidden="true">{item.emoji}</span><span className="subject-arrow" aria-hidden="true">↗</span></span>
                  <span className="subject-name">{item.name}</span>
                  <span className="subject-unit">{item.unit}</span>
                  <span className="progress-track"><span style={{ width: `${subjectProgress[item.id]}%` }} /></span>
                  <span className="progress-label"><strong>{subjectProgress[item.id]}%</strong> of your path explored</span>
                </button>
              ))}
            </div>
          </section>

          <section className="bottom-grid">
            <article className="next-card">
              <div className="next-icon" aria-hidden="true">{subject.emoji}</div>
              <div className="next-copy"><span className="eyebrow">UP NEXT IN {subject.name.toUpperCase()}</span><h3>{subject.next}</h3><p>{subject.detail}</p></div>
              <button className="round-arrow" onClick={openChallenge} aria-label={`Start ${subject.name} activity`}>→</button>
            </article>
            <article className="kindness-card">
              <span className="kindness-spark" aria-hidden="true">✦</span>
              <div className="kindness-label">A LITTLE REMINDER</div>
              <p>“Mistakes help your brain <strong>grow stronger.</strong>”</p>
              <span className="kindness-heart" aria-hidden="true">♡</span>
            </article>
          </section>
          <footer className="page-footer"><span>Made for curious minds</span><span aria-hidden="true">✦</span><span>Keep being wonderfully you!</span></footer>
        </div>
      </main>

      {isChallengeOpen && (
        <div className="modal-backdrop" role="presentation" onMouseDown={(event) => { if (event.target === event.currentTarget) closeChallenge(); }}>
          <section className={`challenge-modal prompt-quest quest-step-${questStep}`} role="dialog" aria-modal="true" aria-labelledby="challenge-title">
            <button className="modal-close" onClick={closeChallenge} aria-label="Close learning quest">×</button>
            {!kidMode && questStep < 4 && <>
              <div className="challenge-progress" aria-label={`Step ${questStep + 1} of 4`}>
                {[0, 1, 2, 3].map((step) => <span key={step} className={questStep >= step ? 'complete' : ''} />)}
              </div>
              <div className="challenge-kicker">🧭 YOUR LEARNING QUEST <span>STEP {questStep + 1} OF 4</span></div>
            </>}

            {kidMode && questStep < 3 && <PromptGame subjects={subjects} activityStyles={activityStyles} supports={learningSupports} level={learningLevel} selectedSubject={selectedSubject} selectedSupports={selectedSupports}
              onGrade={setGradeLevel} onSubject={(id) => { setSelectedSubject(id); setSelectedTopic(subjects.find((x) => x.id === id).next); }} onTopic={setSelectedTopic} onActivity={setSelectedActivity}
              onToggleSupport={toggleSupport} onTricky={setTricky} onOlder={() => { setGradeLevel(4); setKidMode(false); }} onFinish={() => setQuestStep(3)} />}
            {!kidMode && questStep === 0 && <>
              <h2 id="challenge-title">What shall we explore?</h2>
              <p className="quest-intro">Your {learningLevel === 1 ? 'new adventure' : `level ${learningLevel} adventure`} starts with something you’re curious about.</p>
              <label className="quest-label" htmlFor="quest-grade">I’m in grade</label>
              <select id="quest-grade" className="quest-select" value={gradeLevel} onChange={(event) => setGradeLevel(Number(event.target.value))}>
                {[1, 2, 3, 4, 5, 6].map((grade) => <option key={grade} value={grade}>Grade {grade}</option>)}
              </select>
              <div className="quest-subjects" role="group" aria-label="Choose a subject">
                {subjects.map((item) => <button key={item.id} className={`quest-subject ${item.color} ${selectedSubject === item.id ? 'chosen' : ''}`} onClick={() => { setSelectedSubject(item.id); setSelectedTopic(item.next); }} aria-pressed={selectedSubject === item.id}>
                  <span aria-hidden="true">{item.emoji}</span><strong>{item.name}</strong><small>{subjectProgress[item.id]}% explored</small>
                </button>)}
              </div>
              <label className="quest-label" htmlFor="quest-topic">What would you like to learn?</label>
              <select id="quest-topic" className="quest-select" value={selectedTopic} onChange={(event) => setSelectedTopic(event.target.value)}>
                {subject.topics.map((topic) => <option key={topic} value={topic}>{topic}</option>)}
                <option value="Something else">Something else</option>
              </select>
              {selectedTopic === 'Something else' && <input className="quest-text-input" aria-label="Type your topic" placeholder="Type a topic you’re curious about" value={customTopic} onChange={(event) => setCustomTopic(event.target.value)} />}
            </>}

            {!kidMode && questStep === 1 && <>
              <h2 id="challenge-title">How should we learn it?</h2>
              <p className="quest-intro">Pick the kind of activity that sounds fun. There’s no wrong choice!</p>
              <div className="choice-list" role="group" aria-label="Choose an activity style">
                {activityStyles.map((style) => <button key={style.id} className={`choice-card ${selectedActivity === style.id ? 'chosen' : ''}`} onClick={() => setSelectedActivity(style.id)} aria-pressed={selectedActivity === style.id}>
                  <span className="choice-icon" aria-hidden="true">{style.icon}</span><span className="choice-copy"><strong>{style.label}</strong><small>{style.description}</small></span><span className="choice-radio" aria-hidden="true">{selectedActivity === style.id ? '✓' : ''}</span>
                </button>)}
              </div>
              {learningLevel >= 3 && <div className="tricky-block"><p className="quest-label">What feels tricky today? <small>(pick any)</small></p><div className="chip-row" role="group" aria-label="What feels tricky">{trickyOptions.map((o) => <button key={o.id} className={`chip ${tricky.includes(o.id) ? 'chosen' : ''}`} aria-pressed={tricky.includes(o.id)} onClick={() => setTricky((c) => c.includes(o.id) ? c.filter((i) => i !== o.id) : [...c, o.id])}>{o.label}</button>)}</div></div>}
              <div className="quest-progress-note"><span>🌟</span> You’ve already explored {subjectProgress[subject.id]}% of {subject.name} — we’ll build on what you know.</div>
            </>}

            {!kidMode && questStep === 2 && <>
              <h2 id="challenge-title">What helps you learn?</h2>
              <p className="quest-intro">Choose any helpers you like. You can skip this — everyone learns in their own way.</p>
              <div className="choice-list support-list" role="group" aria-label="Optional learning supports">
                {learningSupports.map((support) => <button key={support.id} className={`choice-card ${selectedSupports.includes(support.id) ? 'chosen' : ''}`} onClick={() => toggleSupport(support.id)} aria-pressed={selectedSupports.includes(support.id)}>
                  <span className="choice-icon" aria-hidden="true">{support.icon}</span><span className="choice-copy"><strong>{support.label}</strong></span><span className="choice-radio" aria-hidden="true">{selectedSupports.includes(support.id) ? '✓' : ''}</span>
                </button>)}
              </div>
              <p className="privacy-note">These are learning preferences, not a test or diagnosis. Your grown-up can help you choose.</p>
            </>}

            {questStep === 3 && <>
              <h2 id="challenge-title">Your learning wish is ready!</h2>
              <p className="quest-intro">Here’s what your learning buddy will use to find a helpful lesson.</p>
              <div className="prompt-preview" aria-label="Generated learning prompt"><pre>{learningPrompt}</pre></div>
              {requestError && <p className="request-error" role="alert">{requestError}</p>}
            </>}

            {questStep === 4 && <>
              <div className="answer-celebration" aria-hidden="true">✨</div>
              <div className="challenge-kicker">YOUR {subject.name.toUpperCase()} DISCOVERY <span>LESSON READY</span></div>
              <h2 id="challenge-title">Your learning buddy found this!</h2>
              <div className="generated-lesson" aria-live="polite">{generatedAnswer}</div>
              {answerSources.length > 0 && <div className="source-note">Based on {answerSources.length} curriculum {answerSources.length === 1 ? 'source' : 'sources'}.</div>}
              {answerWarning && <p className="request-error" role="status">This answer may need a grown-up or teacher to check it. Your learning buddy could not fully match it to the curriculum.</p>}
              {!practiceGame && <div className="game-next-step"><span aria-hidden="true">🌱</span><span><strong>Your lesson is ready.</strong><small>I couldn’t make a practice game from this lesson just now. You can try another topic.</small></span></div>}
            </>}

            {questStep === 5 && practiceGame && !isMulti && <GameRenderer game={practiceGame} onDone={finishGame} />}
            {questStep === 5 && practiceGame && isMulti && <>
              <div className="challenge-kicker">🎮 YOUR PRACTICE GAME <span>ONE QUESTION</span></div>
              <h2 id="challenge-title">Show what you discovered!</h2>
              <p className="challenge-question">{practiceGame.question}</p>
              <div className="answer-list" role="group" aria-label="Choose your answer">
                {practiceGame.choices.map((choice, index) => <button key={`${index}-${choice}`} className={`answer-option ${gameChoice === index ? 'chosen' : ''} ${gameChecked && index === practiceGame.correct_index ? 'correct' : ''}`} onClick={() => { if (!gameChecked) setGameChoice(index); }} aria-pressed={gameChoice === index}>
                  <span className="answer-letter">{String.fromCharCode(65 + index)}</span>{choice}
                  {gameChecked && index === practiceGame.correct_index && <span className="answer-check">✓</span>}
                </button>)}
              </div>
              {gameChecked && <div className={`answer-feedback ${gameChoice === practiceGame.correct_index ? 'success' : 'try-again'}`} role="status">{gameChoice === practiceGame.correct_index ? `🌟 You did it! ${practiceGame.explanation}` : `💛 That’s okay! ${practiceGame.explanation}`}</div>}
              {!gameChecked && <button className="hint-button" onClick={() => setRequestError(practiceGame.hint)}>💡 Give me a hint</button>}
              {requestError && questStep === 5 && <p className="hint-note" role="status">{requestError}</p>}
            </>}

            <div className="quest-actions">
              {(!kidMode || questStep === 3) && questStep > 0 && questStep < 4 && <button className="secondary-button" onClick={() => { setRequestError(''); setQuestStep((step) => step - 1); }}>← Back</button>}
              {!kidMode && questStep < 3 && <button className="primary-button modal-submit" disabled={questStep === 0 && selectedTopic === 'Something else' && !customTopic.trim()} onClick={() => setQuestStep((step) => step + 1)}>Next step <span aria-hidden="true">→</span></button>}
              {questStep === 3 && <button className="primary-button modal-submit" onClick={sendPromptToTutor} disabled={isLoadingAnswer}>{isLoadingAnswer ? <><span className="loading-dot" /> Finding your lesson…</> : <>Ask my learning buddy <span aria-hidden="true">→</span></>}</button>}
              {questStep === 4 && practiceGame && <button className="primary-button modal-submit" onClick={() => { setRequestError(''); setGameChoice(null); setGameChecked(false); setQuestStep(5); }}>Play my game <span aria-hidden="true">→</span></button>}
              {questStep === 4 && !practiceGame && <button className="primary-button modal-submit" onClick={closeChallenge}>Back to my garden <span aria-hidden="true">→</span></button>}
              {questStep === 5 && isMulti && !gameChecked && <button className="primary-button modal-submit" disabled={gameChoice === null} onClick={() => setGameChecked(true)}>Check my answer <span aria-hidden="true">→</span></button>}
              {questStep === 5 && isMulti && gameChecked && <button className="primary-button modal-submit" onClick={() => {
                if (gameChoice === practiceGame.correct_index) {
                  setDailyActivities((count) => Math.min(count + 1, 3));
                  setSubjectProgress((progress) => ({ ...progress, [subject.id]: Math.min(progress[subject.id] + 3, 100) }));
                  setExperiencePoints((points) => points + 10);
                }
                closeChallenge();
              }}>Back to my garden <span aria-hidden="true">→</span></button>}
              {!kidMode && questStep === 2 && <button className="skip-button" onClick={() => setQuestStep(3)}>Skip helpers</button>}
            </div>
            {!kidMode && questStep < 4 && <p className="gentle-note">No rush — you’re in charge of your learning adventure.</p>}
          </section>
        </div>
      )}
    </div>
  );
}

export default App;
