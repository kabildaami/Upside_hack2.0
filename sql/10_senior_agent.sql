-- EduNova senior students (grades 7-12). Additive, no destructive resets.
BEGIN;
CREATE TABLE IF NOT EXISTS public.senior_threads (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 mode varchar(24) NOT NULL DEFAULT 'coach' CHECK (mode IN ('coach','culture','goal','hobby')),
 created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS idx_senior_threads_owner ON public.senior_threads(student_id,updated_at DESC);
CREATE TABLE IF NOT EXISTS public.senior_turns (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,thread_id uuid NOT NULL REFERENCES public.senior_threads(id) ON DELETE CASCADE,
 student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 role varchar(12) NOT NULL CHECK(role IN ('student','assistant')), body text NOT NULL,
 source_refs jsonb NOT NULL DEFAULT '[]', created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS idx_senior_turns_owner ON public.senior_turns(student_id,thread_id,id);
CREATE TABLE IF NOT EXISTS public.senior_goals (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 category varchar(16) NOT NULL CHECK(category IN ('academic','hobby','wellbeing','culture')),
 title varchar(200) NOT NULL, milestone text, week_start date NOT NULL, target_count integer NOT NULL DEFAULT 1 CHECK(target_count BETWEEN 1 AND 100),
 completed_count integer NOT NULL DEFAULT 0 CHECK(completed_count >= 0), created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(student_id,category,title,week_start));
CREATE INDEX IF NOT EXISTS idx_senior_goals_student ON public.senior_goals(student_id,week_start);
CREATE TABLE IF NOT EXISTS public.senior_culture_attempts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 challenge_key varchar(80) NOT NULL, answer text NOT NULL, correct boolean NOT NULL,
 hints_used integer NOT NULL DEFAULT 0, created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS public.senior_written_prompts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 document_id integer NOT NULL REFERENCES public.teacher_curriculum_documents(id) ON DELETE CASCADE,
 source_chunk_id integer NOT NULL REFERENCES public.teacher_curriculum_chunks(id) ON DELETE CASCADE,
 prompt text NOT NULL, rubric jsonb NOT NULL, teacher_approved boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS public.senior_written_submissions (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 prompt_id bigint NOT NULL REFERENCES public.senior_written_prompts(id) ON DELETE CASCADE,
 reasoning_steps jsonb NOT NULL DEFAULT '[]', written_answer text NOT NULL,
 feedback jsonb NOT NULL DEFAULT '{}', submitted_at timestamptz NOT NULL DEFAULT now());
-- Diary ciphertext only; no diary content in regular chat, parent or teacher APIs.
CREATE TABLE IF NOT EXISTS public.senior_diary (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 ciphertext bytea NOT NULL, created_at timestamptz NOT NULL DEFAULT now());
CREATE INDEX IF NOT EXISTS idx_senior_diary_owner ON public.senior_diary(student_id,created_at DESC);
CREATE TABLE IF NOT EXISTS public.senior_trusted_contacts (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 contact_name varchar(120) NOT NULL, relationship varchar(40) NOT NULL,
 contact_information varchar(255), priority integer NOT NULL DEFAULT 1 CHECK(priority BETWEEN 1 AND 10),
 is_safe_to_contact boolean NOT NULL DEFAULT false,
 created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS public.senior_safety_requests (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), student_id integer NOT NULL REFERENCES public.students(student_id) ON DELETE CASCADE,
 category varchar(32) NOT NULL CHECK(category IN ('self_harm','violence','abuse','other_urgent')),
 contact_id bigint REFERENCES public.senior_trusted_contacts(id) ON DELETE SET NULL,
 status varchar(24) NOT NULL DEFAULT 'requested' CHECK(status IN ('requested','reviewing','resolved')),
 created_at timestamptz NOT NULL DEFAULT now());
-- A recorded request is NOT a sent notification. Human-led safeguarding required.
COMMIT;

-- Optional teacher-reviewed entity-level learning metadata, one concept per source chunk.
CREATE TABLE IF NOT EXISTS public.senior_chunk_entities (
 id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
 chunk_id integer NOT NULL REFERENCES public.teacher_curriculum_chunks(id) ON DELETE CASCADE,
 entity_type varchar(30) NOT NULL CHECK(entity_type IN ('concept','definition','prerequisite','worked_step','historical_person','place','economic_term','misconception')),
 name varchar(180) NOT NULL,
 description text NOT NULL,
 learning_objective text,
 evidence_excerpt text,
 created_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(chunk_id,entity_type,name)
);
CREATE INDEX IF NOT EXISTS idx_senior_entities_chunk ON public.senior_chunk_entities(chunk_id);
