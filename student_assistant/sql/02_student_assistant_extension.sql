-- ADDITIVE MIGRATION: run AFTER the existing public school schema.
-- Does not drop or recreate any user/school/student/survey records.
BEGIN;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS assistant;

CREATE TABLE IF NOT EXISTS assistant.student_settings (
 student_id integer PRIMARY KEY REFERENCES public.students(student_id) ON DELETE CASCADE,
 age_variant text NOT NULL DEFAULT 'junior' CHECK(age_variant IN ('junior','senior')),
 locale text NOT NULL DEFAULT 'en', timezone text NOT NULL DEFAULT 'Africa/Tunis',
 preferred_explanation text, preferred_activity_minutes integer NOT NULL DEFAULT 12 CHECK(preferred_activity_minutes BETWEEN 5 AND 35),
 pacing_opt_in boolean NOT NULL DEFAULT false, memory_opt_in boolean NOT NULL DEFAULT false,
 parent_teacher_reviewed boolean NOT NULL DEFAULT false,
 updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS assistant.student_consents (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 purpose text NOT NULL CHECK(purpose IN ('learning_memory','pacing_analytics','curriculum_processing')),
 granted boolean NOT NULL, granted_by_user_id integer REFERENCES public.users(user_id),
 recorded_at timestamptz NOT NULL DEFAULT now(), UNIQUE(student_id,purpose)
);
CREATE TABLE IF NOT EXISTS assistant.course_documents (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 filename text NOT NULL, file_sha256 text NOT NULL UNIQUE,
 title text NOT NULL, subject text NOT NULL, grade_level text NOT NULL DEFAULT '3rd primary',
 source_type text NOT NULL DEFAULT 'teacher_material', storage_path text NOT NULL,
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS assistant.course_chunks (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 document_id bigint NOT NULL REFERENCES assistant.course_documents(id) ON DELETE CASCADE,
 chunk_index integer NOT NULL, page_number integer NOT NULL,
 adventure_no integer, heading text, content text NOT NULL,
 content_tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED,
 embedding vector(384),
 UNIQUE(document_id,chunk_index)
);
CREATE INDEX IF NOT EXISTS idx_course_tsv ON assistant.course_chunks USING gin(content_tsv);
CREATE INDEX IF NOT EXISTS idx_course_vector ON assistant.course_chunks USING hnsw(embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_course_subject ON assistant.course_documents(subject,grade_level);

CREATE TABLE IF NOT EXISTS assistant.learning_sessions (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 thread_id text NOT NULL, topic text, subject text,
 started_at timestamptz NOT NULL DEFAULT now(), ended_at timestamptz,
 active_seconds integer NOT NULL DEFAULT 0 CHECK(active_seconds>=0), idle_seconds integer NOT NULL DEFAULT 0 CHECK(idle_seconds>=0),
 break_seconds integer NOT NULL DEFAULT 0 CHECK(break_seconds>=0),
 status text NOT NULL DEFAULT 'active' CHECK(status IN ('active','finished','abandoned'))
);
CREATE INDEX IF NOT EXISTS idx_session_student ON assistant.learning_sessions(student_id,started_at DESC);
CREATE TABLE IF NOT EXISTS assistant.activity_events (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 session_id uuid NOT NULL REFERENCES assistant.learning_sessions(id) ON DELETE CASCADE,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 event_type text NOT NULL CHECK(event_type IN ('activity_started','activity_completed','hint_requested','answer_submitted','break_started','break_ended','student_feedback','idle_observed')),
 duration_seconds integer CHECK(duration_seconds BETWEEN 0 AND 7200), payload jsonb NOT NULL DEFAULT '{}', occurred_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_event_student ON assistant.activity_events(student_id,occurred_at DESC);
CREATE TABLE IF NOT EXISTS assistant.conversation_turns (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 thread_id text NOT NULL, session_id uuid REFERENCES assistant.learning_sessions(id) ON DELETE SET NULL,
 role text NOT NULL CHECK(role IN ('student','assistant')),
 message text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_turns_thread ON assistant.conversation_turns(student_id,thread_id,created_at DESC);
CREATE TABLE IF NOT EXISTS assistant.learning_memories (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 category text NOT NULL CHECK(category IN ('learning_preference','learning_progress','concept_gap','successful_strategy')),
 content text NOT NULL, evidence_count integer NOT NULL DEFAULT 1,
 confidence numeric(4,3) NOT NULL DEFAULT 0.5 CHECK(confidence BETWEEN 0 AND 1),
 source_session_id uuid REFERENCES assistant.learning_sessions(id) ON DELETE SET NULL,
 embedding vector(384), active boolean NOT NULL DEFAULT true,
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now(),
 expires_at timestamptz
);
CREATE INDEX IF NOT EXISTS idx_memory_student ON assistant.learning_memories(student_id,active);
CREATE INDEX IF NOT EXISTS idx_memory_vector ON assistant.learning_memories USING hnsw(embedding vector_cosine_ops);
CREATE TABLE IF NOT EXISTS assistant.concept_mastery (
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 subject text NOT NULL, concept_key text NOT NULL,
 attempts integer NOT NULL DEFAULT 0, correct integer NOT NULL DEFAULT 0,
 independent_correct integer NOT NULL DEFAULT 0, hints_used integer NOT NULL DEFAULT 0,
 mastery_score numeric(4,3) NOT NULL DEFAULT 0.5 CHECK(mastery_score BETWEEN 0 AND 1),
 last_practiced_at timestamptz, next_review_on date,
 PRIMARY KEY(student_id,subject,concept_key)
);
CREATE TABLE IF NOT EXISTS assistant.quiz_items (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 subject text NOT NULL, concept_key text NOT NULL, source_chunk_id bigint REFERENCES assistant.course_chunks(id),
 question text NOT NULL, options jsonb NOT NULL, answer_index integer NOT NULL,
 hint text, difficulty integer NOT NULL DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 5),
 status text NOT NULL DEFAULT 'draft' CHECK(status IN ('draft','validated','reviewed')),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS assistant.quiz_attempts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 quiz_item_id uuid NOT NULL REFERENCES assistant.quiz_items(id) ON DELETE CASCADE,
 session_id uuid REFERENCES assistant.learning_sessions(id) ON DELETE SET NULL,
 selected_index integer, is_correct boolean NOT NULL, hints_used integer NOT NULL DEFAULT 0,
 response_seconds integer CHECK(response_seconds BETWEEN 0 AND 7200),
 answered_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(student_id,quiz_item_id)
);
CREATE TABLE IF NOT EXISTS assistant.study_goals (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 subject text NOT NULL, goal text NOT NULL, target_date date NOT NULL,
 status text NOT NULL DEFAULT 'planned' CHECK(status IN ('planned','in_progress','done','skipped')),
 created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_study_goals ON assistant.study_goals(student_id,target_date);
CREATE TABLE IF NOT EXISTS assistant.hobby_recommendations (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 hobby_label text NOT NULL, score numeric(4,3) NOT NULL CHECK(score BETWEEN 0 AND 1),
 reason text NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS assistant.agent_audit (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 student_id integer REFERENCES public.students(student_id) ON DELETE SET NULL,
 action text NOT NULL, outcome text NOT NULL, details jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL DEFAULT now()
);
-- Defense-in-depth RLS: app should connect with a dedicated restricted role,
-- not postgres/superuser; policies here intentionally deny direct student-table access.
ALTER TABLE assistant.learning_memories ENABLE ROW LEVEL SECURITY;
ALTER TABLE assistant.conversation_turns ENABLE ROW LEVEL SECURITY;
ALTER TABLE assistant.activity_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE assistant.quiz_attempts ENABLE ROW LEVEL SECURITY;
-- Set up a dedicated service role and audited policies for production tenant auth.
COMMIT;

-- Keep hobbies available for the 13–18 discovery workflow. Safe incremental seeds.
INSERT INTO public.hobbies(label) VALUES
 ('Robotics'),('Photography'),('Creative writing'),('Chess'),('Cooking'),('Gardening'),
 ('Debate'),('Astronomy'),('Hiking'),('Digital design'),('Learning languages')
ON CONFLICT(label) DO NOTHING;
