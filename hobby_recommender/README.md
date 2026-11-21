# HobbyQuest — AI Hobby Recommender (ages 13–18)

A working browser-based 6-question hobby recommender, seeded with **40 curated, diverse hobbies** in **SQLite**. Uses **OpenRouter `openai/gpt-4o-mini`** for structured NLP preference extraction, then computes **deterministic, auditable scores** and returns 5 suggested hobbies. A simplified local NLP fallback is available without an API key.

## Quickstart (Python 3.10+)

```bash
cd hobby_recommender
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env  # On Windows: copy .env.example .env
# Edit .env and set OPENROUTER_API_KEY=your_key_here
python -m app.catalog
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000** and answer six free-text questions.

SQLite database is already included at `data/hobbies.sqlite3`; `python -m app.catalog` creates/refreshes it. The API also initializes it on startup.

## API

- `GET /` — responsive web questionnaire + results
- `GET /api/questions` — six prompts
- `GET /api/hobbies` — complete 40-row catalog
- `POST /api/recommend` — JSON payload `{"answers":["text1","text2","text3","text4","text5","text6"]}`
- `GET /health` — health check
- `GET /docs` — generated API documentation

## Data model

SQLite table `hobbies` has: `id`, `name`, `category`, `description`, `tags`, `traits`, `environment`, `social_mode`, `physical_intensity`, `estimated_cost`, `equipment`, `accessibility_notes`. Comma-delimited `tags` and `traits` are returned as arrays in JSON; production could normalize them into join tables. Categories include Technology, Strategy, Science, Culture, Literature, Visual Arts, Crafts, Music, Performing Arts, Media, Team Sports, Individual Sports, Wellness, Outdoor Adventure, Nature, Life Skills, Communication, Community.

## Algorithm

**1. Six free-text inputs:** interests, strengths, social preference, location/pacing, goals, constraints.

**2. Extract preferences:** GPT-4o mini through OpenRouter chat completions in JSON mode (`response_format: json_object`) produces a structured preference profile: 16 weighted dimensions (`0..1`), interests, explicit dislikes, setting, social format, intensity, budget, and a short summary. Untrusted questionnaire answers are treated as data. Schema values are validated/clamped server-side. No medical, personality, or psychological conclusions.

**3. Rank catalog:** for each row:

- up to **65** points: weighted overlap between the user's inferred dimensions and the hobby's traits; normalized by total positive user weights
- up to **20** points: explicit keyword overlap in name/tags/description
- up to **15** points: practical compatibility (penalties for mismatched social format, setting, intensity, and cost)
- explicit rejected topics in hobby names/categories/tags are **excluded**
- total clipped to 0–100; sorted by score descending, name as tie-breaker; show top 5 with score breakdown, reasons and getting-started details.

**Important:** 0–100 scores are heuristic *match scores*, not calibrated probabilities, academic assessments, clinical measures, or predictions of ability. Weights are initial product assumptions; tune only after pilot testing and evaluating fairness, accessibility, and actual user satisfaction. In particular, lack of evidence for an interest is not a dislike. Results are explainable and the entire catalog remains browsable.

**4. Offline fallback:** If the key is missing or OpenRouter fails, an uncomplicated English keyword parser produces approximate weights. It is less accurate with paraphrases and nuanced negatives. Responses explicitly indicate whether the LLM or fallback was used. Never present fallback as AI-powered semantic extraction.

## Security and privacy

- API keys stay in the server-side `.env` file; `.env` is gitignored. Never expose secrets to JS.
- Six submitted answers are processed in memory and **not stored** in the SQLite database. If OpenRouter is configured, questionnaire responses are transmitted to OpenRouter and its routed model provider, subject to their policies. Obtain required minor/guardian consent and provide disclosures before deploying to real teens.
- Do not solicit sensitive personal data, medical details or precise locations. API responses should never be used to diagnose or label students.
- This is a development prototype, not a production-ready minor-facing service. Add HTTPS, authentication, rate limits, logging redaction, data retention controls, moderation where appropriate, consent workflows, accessibility assessment and evaluation prior to deployment.
- No account creation, usage tracking, advertisements, or engagement-pressure mechanisms.

## Testing

```bash
pytest -q
```

## Project layout

```
hobby_recommender/
├── app/
│   ├── __init__.py
│   ├── catalog.py         # 40 curated records, SQLite schema, seed/retrieval
│   ├── recommender.py     # NLP extraction, validation, deterministic scoring
│   └── main.py            # FastAPI endpoints
├── static/
│   └── index.html         # responsive six-step quiz, recommendations, full catalog
├── data/
│   └── hobbies.sqlite3   # actual populated database
├── tests/
│   └── test_recommender.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Production enhancements

Add admin-manageable hobby metadata and multilingual tagging, hybrid embeddings + categorical ranking, age-specific affordances, education-aware cold-start questions, optional student feedback, audited scoring evaluations, and privacy-preserving analytics. Avoid hard predictions of identity or aptitude from a short questionnaire.
